import csv
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from dateutil import parser


class ReceiptStore:
    CSV_HEADERS = [
        "id",
        "created_at",
        "date",
        "vendor",
        "total",
        "tax",
        "image_path",
        "raw_text",
    ]

    def __init__(self, csv_path: str, sqlite_path: Optional[str] = None):
        self.csv_path = csv_path
        self.sqlite_path = sqlite_path
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        self._ensure_csv()
        if sqlite_path:
            os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
            self._ensure_sqlite()

    def _ensure_csv(self) -> None:
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
                writer.writeheader()

    def _ensure_sqlite(self) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    date TEXT,
                    vendor TEXT,
                    total REAL,
                    tax REAL,
                    image_path TEXT,
                    raw_text TEXT
                );
                """
            )
            conn.commit()

    def _load_csv(self) -> List[Dict[str, str]]:
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _write_csv(self, rows: List[Dict[str, str]]) -> None:
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def _write_sqlite(self, rows: List[Dict[str, str]]) -> None:
        if not self.sqlite_path:
            return
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute("DELETE FROM receipts")
            conn.executemany(
                """
                INSERT OR REPLACE INTO receipts (
                    id, created_at, date, vendor, total, tax, image_path, raw_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        row["id"],
                        row["created_at"],
                        row.get("date", ""),
                        row.get("vendor", ""),
                        float(row.get("total", 0) or 0),
                        float(row.get("tax", 0) or 0),
                        row.get("image_path", ""),
                        row.get("raw_text", ""),
                    )
                    for row in rows
                ],
            )
            conn.commit()

    def list_receipts(
        self, search: Optional[str] = None, sort_by: str = "created_at", descending: bool = True
    ) -> List[Dict[str, str]]:
        rows = self._load_csv()
        if search:
            lower = search.lower()
            rows = [
                r
                for r in rows
                if lower in r.get("vendor", "").lower()
                or lower in r.get("raw_text", "").lower()
                or lower in r.get("date", "").lower()
            ]
        rows.sort(key=lambda r: r.get(sort_by, ""), reverse=descending)
        return rows

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, str]]:
        for row in self._load_csv():
            if row["id"] == receipt_id:
                return row
        return None

    def add_receipt(self, data: Dict[str, str]) -> Dict[str, str]:
        receipt = {
            "id": data.get("id", str(uuid.uuid4())),
            "created_at": datetime.utcnow().isoformat(),
            "date": data.get("date", ""),
            "vendor": data.get("vendor", ""),
            "total": self._normalize_number(data.get("total")),
            "tax": self._normalize_number(data.get("tax")),
            "image_path": data.get("image_path", ""),
            "raw_text": data.get("raw_text", ""),
        }
        rows = self._load_csv()
        rows.append(receipt)
        self._write_csv(rows)
        self._write_sqlite(rows)
        return receipt

    def update_receipt(self, receipt_id: str, updates: Dict[str, str]) -> Optional[Dict[str, str]]:
        rows = self._load_csv()
        updated = None
        for row in rows:
            if row["id"] == receipt_id:
                row.update(
                    {
                        "date": updates.get("date", row.get("date", "")),
                        "vendor": updates.get("vendor", row.get("vendor", "")),
                        "total": self._normalize_number(updates.get("total", row.get("total", ""))),
                        "tax": self._normalize_number(updates.get("tax", row.get("tax", ""))),
                        "raw_text": updates.get("raw_text", row.get("raw_text", "")),
                        "image_path": updates.get("image_path", row.get("image_path", "")),
                    }
                )
                updated = row
                break
        if updated:
            self._write_csv(rows)
            self._write_sqlite(rows)
        return updated

    def _normalize_number(self, value: Optional[str]) -> str:
        if value is None:
            return ""
        text = str(value).strip().replace("$", "").replace(",", "")
        if not text:
            return ""
        try:
            return f"{float(text):.2f}"
        except ValueError:
            return value

    @staticmethod
    def parse_date(text: str) -> str:
        try:
            return parser.parse(text, fuzzy=True).date().isoformat()
        except (ValueError, TypeError):
            return ""

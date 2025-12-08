import os
from pathlib import Path
from typing import Optional

from flask import Flask, redirect, render_template, request, send_file, send_from_directory, url_for

from camera import capture_image
from data_store import ReceiptStore
from ocr import run_ocr

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "receipts.csv"
SQLITE_PATH = DATA_DIR / "receipts.db"

app = Flask(__name__)
store = ReceiptStore(csv_path=str(CSV_PATH), sqlite_path=str(SQLITE_PATH))


def get_battery_status() -> Optional[str]:
    log_path = DATA_DIR / "battery.log"
    if not log_path.exists():
        return None
    try:
        *_, last = log_path.read_text().splitlines()
        return last
    except ValueError:
        return None


@app.route("/")
def dashboard():
    receipts = store.list_receipts()
    total_sum = sum(float(r.get("total", 0) or 0) for r in receipts)
    tax_sum = sum(float(r.get("tax", 0) or 0) for r in receipts)
    battery_line = get_battery_status()
    return render_template(
        "index.html",
        count=len(receipts),
        total_sum=total_sum,
        tax_sum=tax_sum,
        battery_line=battery_line,
    )


@app.route("/receipts")
def receipts_table():
    search = request.args.get("search")
    sort_by = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")
    receipts = store.list_receipts(search=search, sort_by=sort_by, descending=order != "asc")
    return render_template("receipts.html", receipts=receipts, search=search, sort_by=sort_by, order=order)


@app.route("/receipts/<receipt_id>", methods=["GET", "POST"])
def receipt_detail(receipt_id):
    receipt = store.get_receipt(receipt_id)
    if not receipt:
        return "Receipt not found", 404
    if request.method == "POST":
        updates = {
            "vendor": request.form.get("vendor", ""),
            "date": request.form.get("date", ""),
            "total": request.form.get("total", ""),
            "tax": request.form.get("tax", ""),
            "raw_text": request.form.get("raw_text", ""),
        }
        updated = store.update_receipt(receipt_id, updates)
        if updated:
            return redirect(url_for("receipt_detail", receipt_id=receipt_id))
    return render_template("receipt_detail.html", receipt=receipt)


@app.route("/scan", methods=["GET", "POST"])
def scan_receipt():
    if request.method == "POST":
        image_path = capture_image(str(IMAGES_DIR))
        data = run_ocr(image_path)
        receipt = store.add_receipt(data)
        return redirect(url_for("receipt_detail", receipt_id=receipt["id"]))
    return render_template("scan.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_receipt():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "No file provided", 400
        filename = file.filename or "uploaded.jpg"
        save_path = IMAGES_DIR / filename
        os.makedirs(IMAGES_DIR, exist_ok=True)
        file.save(save_path)
        data = run_ocr(str(save_path))
        receipt = store.add_receipt(data)
        return redirect(url_for("receipt_detail", receipt_id=receipt["id"]))
    return render_template("upload.html")


@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/export/csv")
def export_csv():
    return send_file(str(CSV_PATH), as_attachment=True, download_name="receipts.csv")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)

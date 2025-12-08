import re
from typing import Dict

import cv2
import numpy as np
import pytesseract
from PIL import Image

from data_store import ReceiptStore


def preprocess_image(image_path: str) -> Image.Image:
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpen = cv2.filter2D(thresh, -1, sharpen_kernel)
    return Image.fromarray(sharpen)


def run_ocr(image_path: str) -> Dict[str, str]:
    cleaned = preprocess_image(image_path)
    text = pytesseract.image_to_string(cleaned)
    data = extract_fields(text)
    data["raw_text"] = text
    data["image_path"] = image_path
    return data


def extract_fields(text: str) -> Dict[str, str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    vendor = lines[0] if lines else ""

    date_match = re.search(
        r"((?:19|20)\d{2}[\-/]\d{1,2}[\-/]\d{1,2})|((?:\d{1,2}[\-/]){2}(?:19|20)\d{2})",
        text,
    )
    alt_date_match = re.search(r"(\d{1,2}[A-Za-z]{3}\d{2,4})", text)
    date_raw = ""
    if date_match:
        date_raw = date_match.group(0)
    elif alt_date_match:
        date_raw = alt_date_match.group(0)
    date = ReceiptStore.parse_date(date_raw)

    total_match = _match_amount(text, labels=["total", "amount", "balance"])
    tax_match = _match_amount(text, labels=["tax", "vat"])

    return {
        "vendor": vendor,
        "date": date,
        "total": total_match or "",
        "tax": tax_match or "",
    }


def _match_amount(text: str, labels):
    pattern = r"(?:{}):?\s*([$€£]?\d+[\d,]*\.\d{{2}})".format("|".join(labels))
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    numbers = re.findall(r"([$€£]?\d+[\d,]*\.\d{2})", text)
    if numbers:
        return numbers[-1]
    return None

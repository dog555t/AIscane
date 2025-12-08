import os
from pathlib import Path
from typing import Optional

from flask import Flask, redirect, render_template, request, send_file, send_from_directory, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from auth import User, UserStore
from camera import capture_image
from data_store import ReceiptStore
from ocr import run_ocr

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "receipts.csv"
SQLITE_PATH = DATA_DIR / "receipts.db"
USERS_PATH = DATA_DIR / "users.json"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

store = ReceiptStore(csv_path=str(CSV_PATH), sqlite_path=str(SQLITE_PATH))
user_store = UserStore(str(USERS_PATH))


@login_manager.user_loader
def load_user(user_id):
    return user_store.get_user(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        if user_store.verify_user(username, password):
            user = user_store.get_user(username)
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not user_store.verify_user(current_user.username, current_password):
            flash("Current password is incorrect", "danger")
        elif new_password != confirm_password:
            flash("New passwords do not match", "danger")
        elif len(new_password) < 6:
            flash("Password must be at least 6 characters", "danger")
        else:
            user_store.change_password(current_user.username, new_password)
            flash("Password changed successfully", "success")
            return redirect(url_for("dashboard"))
    
    return render_template("change_password.html")


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
@login_required
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
@login_required
def receipts_table():
    search = request.args.get("search")
    sort_by = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")
    receipts = store.list_receipts(search=search, sort_by=sort_by, descending=order != "asc")
    return render_template("receipts.html", receipts=receipts, search=search, sort_by=sort_by, order=order)


@app.route("/receipts/<receipt_id>", methods=["GET", "POST"])
@login_required
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
@login_required
def scan_receipt():
    if request.method == "POST":
        image_path = capture_image(str(IMAGES_DIR))
        data = run_ocr(image_path)
        receipt = store.add_receipt(data)
        return redirect(url_for("receipt_detail", receipt_id=receipt["id"]))
    return render_template("scan.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
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
@login_required
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/export/csv")
@login_required
def export_csv():
    return send_file(str(CSV_PATH), as_attachment=True, download_name="receipts.csv")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)

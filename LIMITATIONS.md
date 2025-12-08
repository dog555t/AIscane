# Limitations and Assumptions

- The MakerFocus UPS V3Plus battery data format is assumed; verify I2C register mapping and adjust `battery_monitor.py` if your hardware differs.
- OCR accuracy depends on Tesseract/EasyOCR language data and lighting; receipts with unusual layouts may need extra preprocessing tweaks in `ocr.py`.
- Hotspot setup files target Raspberry Pi OS with hostapd + dnsmasq; alternative network managers may require manual adaptation.
- The web app is designed for trusted local networks/hotspot use and includes minimal authentication; add access controls for shared environments.
- Camera capture uses `libcamera-still`; if unavailable, update `camera.py` to match your camera stack.
- File paths default to the project directory; ensure adequate storage and permissions when writing images, CSV, or SQLite data.

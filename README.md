# Raspberry Pi Receipt Scanner (Offline Hotspot)

[![Download Latest Image](https://img.shields.io/github/v/release/dog555t/AIscane?label=Download%20Standalone%20Image)](https://github.com/dog555t/AIscane/releases/latest) 

This project turns a Raspberry Pi 5 + AI Camera Module into a self-contained receipt scanner. It captures receipts with `libcamera`, runs OCR, stores structured data in CSV (and SQLite), exposes a local Flask UI, and can broadcast its own Wi‑Fi hotspot so users can connect directly without a router. A MakerFocus UPS battery monitor handles safe shutdowns.

> 🚀 **Quick Start**: Download the [pre-built standalone image](https://github.com/dog555t/AIscane/releases/latest) and flash it with [Raspberry Pi Imager](https://www.raspberrypi.com/software/). See [STANDALONE_IMAGE.md](STANDALONE_IMAGE.md) for complete instructions.

## Features
- One-click capture via `/scan` or upload existing images via `/upload`.
- OCR (Tesseract) extracts vendor, date, total, tax, and stores raw text.
- Data saved to `data/receipts.csv` and mirrored to `data/receipts.db` (SQLite).
- Web UI (Bootstrap): dashboard, searchable/sortable table, detail & edit view, CSV export.
- Hotspot on `192.168.4.1` with captive redirect to the web app.
- Battery watchdog reads the MakerFocus UPS over I²C, logs %, and triggers safe shutdown below 10%.

## Folder Layout
```
app.py                  # Flask entrypoint
camera.py               # libcamera capture helper
ocr.py                  # OCR + parsing helpers
data_store.py          # CSV/SQLite storage
battery_monitor.py      # UPS monitor loop
requirements.txt        # Python dependencies
config/hotspot/*        # hostapd + dnsmasq + dhcpcd configs and iptables helper
services/*.service      # systemd units for the web app & battery monitor
templates/              # HTML templates
```

## Prerequisites
- Raspberry Pi OS Bookworm (tested with Pi 5) and the Raspberry Pi AI Camera Module.
- `libcamera-still` available (installed by default on modern Pi OS).
- `tesseract-ocr` package: `sudo apt-get install tesseract-ocr -y`.
- Python 3.11+ with pip.
- MakerFocus Raspberry Pi 4 Battery Pack UPS V3Plus connected via I²C (fuel-gauge address 0x36 assumed).

## Install Python environment
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv tesseract-ocr libtesseract-dev libatlas-base-dev libopenjp2-7 libjpeg-dev
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the web app manually
```bash
source .venv/bin/activate
python app.py
```
Visit http://127.0.0.1:5000 (or http://192.168.4.1 when on the hotspot).

## Quick Start with Pre-built Image (Recommended)

The fastest way to get started is using the pre-built standalone image:

1. **Download the latest image** from [Releases](https://github.com/dog555t/AIscane/releases/latest)
2. **Flash to SD card** using [Raspberry Pi Imager](https://www.raspberrypi.com/software/):
   - Choose "Use custom" and select the downloaded `.img.xz` file
   - Select your SD card and click "Write"
3. **Boot your Raspberry Pi** with the flashed SD card
4. **Connect to Wi-Fi**: SSID `Receipt-Scanner`, password `receipt1234`
5. **Open browser** and navigate to `http://192.168.4.1`

Default login: username `pi`, password `raspberry` (⚠️ change after first login!)

The pre-built image includes everything configured and ready to use.

<< codex/build-raspberry-pi-receipt-scanner-project-q6udip
## Build a flashable image (pi-gen)
You can produce a ready-to-boot Raspberry Pi OS image with everything preinstalled using the `image/` folder and `pi-gen`.

### Automated Build (Recommended)
```bash
cd image
./build-image.sh
```

The script will:
- Clone/update pi-gen
- Configure the build
- Create a compressed `.img.xz` image
- Generate SHA256 checksums

### Manual Build
1. Clone `pi-gen` and copy this repo's stage/config:
   ```bash
   git clone https://github.com/RPi-Distro/pi-gen.git
   cd pi-gen
   cp /path/to/repo/image/pi-gen-config config
   cp -r /path/to/repo/image/stage-receipt-scanner .
   export RECEIPT_SCANNER_SRC=/path/to/repo
   sudo env RECEIPT_SCANNER_SRC="$RECEIPT_SCANNER_SRC" ./build.sh
   ```
2. Flash the resulting `deploy/receipt-scanner*.img.xz` to an SD card.

The stage installs dependencies, copies the app to `/home/pi/receipt-scanner`, enables the web app + battery monitor services, and configures the hotspot/NAT service automatically. For more details see `image/README.md`.

### CI/CD Automated Builds
Images are automatically built and released via GitHub Actions when a version tag is pushed:
```bash
git tag v1.0.0
git push origin v1.0.0
```

=======
>> main
## Configure the Wi‑Fi hotspot (hostapd + dnsmasq + dhcpcd)
1. Install services:
```bash
sudo apt-get install -y hostapd dnsmasq
sudo systemctl stop hostapd dnsmasq
```
2. Copy configs:
```bash
sudo cp config/hotspot/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp config/hotspot/dnsmasq.conf /etc/dnsmasq.conf
sudo cp config/hotspot/routed-ap.conf /etc/dhcpcd.conf.d/receipt-ap.conf
```
3. Point hostapd default config:
```bash
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee /etc/default/hostapd
```
4. Enable IP forwarding + NAT:
```bash
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
sudo bash config/hotspot/iptables.sh
```
<< codex/build-raspberry-pi-receipt-scanner-project-q6udip
You can also enable the provided systemd unit to enforce the NAT rules at boot:
```bash
sudo cp services/hotspot_nat.service /etc/systemd/system/
sudo cp config/hotspot/iptables.sh /usr/local/sbin/receipt-iptables.sh
sudo chmod +x /usr/local/sbin/receipt-iptables.sh
sudo systemctl daemon-reload
sudo systemctl enable --now hotspot_nat.service
```
=======
>> main
5. Restart services:
```bash
sudo systemctl restart dhcpcd
sudo systemctl start hostapd
sudo systemctl start dnsmasq
```
The Pi now advertises SSID `Receipt-Scanner` (password `receipt1234`) and hands out DHCP in `192.168.4.0/24`. All DNS resolves to `192.168.4.1` so browsers land on the web UI.

### Optional: NetworkManager approach (Bookworm desktop)
Add a connection profile `/etc/NetworkManager/system-connections/receipt-scanner.nmconnection` with mode `ap`, SSID `Receipt-Scanner`, security WPA2, and IPv4 shared mode with address `192.168.4.1/24` if you prefer NM instead of hostapd/dnsmasq.

## Autostart with systemd
Assuming the project lives in `/home/pi/receipt-scanner`:
```bash
sudo cp services/receipt_scanner.service /etc/systemd/system/
sudo cp services/battery_monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now receipt_scanner.service
sudo systemctl enable --now battery_monitor.service
```
Logs write to `/var/log/receipt_scanner*.log` and `/var/log/battery_monitor*.log`. Update paths inside the unit files if you keep the code elsewhere.

## Battery monitor details
- Uses I²C fuel gauge at address `0x36` (MAX17043/44 typical for MakerFocus UPS).
- Logs percentage and voltage every 60s to `data/battery.log`.
- Initiates `sudo shutdown -h now` when percentage <= 10% to avoid corruption. Adjust `LOW_BATTERY_THRESHOLD` or `CHECK_INTERVAL` in `battery_monitor.py` to taste.

## Capturing + OCR flow
1. `/scan` calls `libcamera-still` for a 1280×960 JPEG saved under `data/images/`.
2. `ocr.run_ocr` pre-processes (grayscale, Otsu threshold, sharpen) and runs Tesseract.
3. Regex heuristics pull date, total, and tax; vendor defaults to the first non-empty line.
4. Data is appended to `receipts.csv` (and mirrored to SQLite) with a UUID.

## CSV/SQLite schema
Fields: `id`, `created_at` (UTC ISO), `date`, `vendor`, `total`, `tax`, `image_path`, `raw_text`.

## Tuning tips
- Improve OCR by adding a white background under receipts and avoiding shadows.
- Install language packs for Tesseract as needed (e.g., `tesseract-ocr-eng` is default).
- If EasyOCR is preferred, swap the `pytesseract.image_to_string` call in `ocr.py` with EasyOCR’s pipeline.

## Safe shutdown test
Unplug AC and watch `tail -f data/battery.log`; when percent dips below 10% the Pi should log the shutdown message and power off safely.

## Backing up data
- Export from `/export/csv`.
- Copy `data/receipts.db` for SQLite.
- Images live in `data/images/`.

## Notes
- The Flask debug server is fine for single-user hotspot use. Swap for `gunicorn` if you expect higher load.
- The `camera.py` helper saves a placeholder gray image if `libcamera` is missing; this keeps the UI usable for development without hardware.

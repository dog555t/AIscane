# Flashable Image Builder

This folder contains a minimal `pi-gen` stage so you can create a ready-to-boot Raspberry Pi OS image with the receipt scanner preinstalled, hotspot enabled, and services auto-starting on first boot.

## Prerequisites
- Debian/Ubuntu host with `git`, `rsync`, `qemu-user-static`, and other `pi-gen` prerequisites.
- `pi-gen` cloned locally (https://github.com/RPi-Distro/pi-gen) with default stages enabled through stage5.
- This repository checked out on the host.
- The build process must run as `root` because `pi-gen` uses loop devices.

## Quick build steps
1. Clone pi-gen and copy the provided config and stage:
   ```bash
   git clone https://github.com/RPi-Distro/pi-gen.git
   cd pi-gen
   cp /path/to/receipt-scanner/image/pi-gen-config config
   cp -r /path/to/receipt-scanner/image/stage-receipt-scanner .
   ```
2. Export the absolute path to this repository so the stage can copy the code into `/home/pi/receipt-scanner` inside the image:
   ```bash
   export RECEIPT_SCANNER_SRC=/path/to/receipt-scanner
   ```
3. Build the image (takes 20–40 minutes depending on host speed):
   ```bash
   sudo env RECEIPT_SCANNER_SRC="$RECEIPT_SCANNER_SRC" ./build.sh
   ```
4. The finished image will appear under `deploy/` (e.g., `deploy/receipt-scanner.img` or `.zip`). Flash it to an SD card using Raspberry Pi Imager or `dd` and boot your Pi.

## What the stage configures
- Installs Python, Tesseract, hostapd, dnsmasq, SQLite, and dependencies.
- Copies this repository into `/home/pi/receipt-scanner`, sets permissions, and builds a virtual environment with `pip install -r requirements.txt`.
- Deploys hotspot config files, enables hostapd + dnsmasq, turns on IPv4 forwarding, and installs an idempotent NAT service that runs `/usr/local/sbin/receipt-iptables.sh` on boot.
- Enables systemd units for the web app (`receipt_scanner.service`) and battery monitor (`battery_monitor.service`).

## Notes
- Default credentials match `pi-gen` defaults (`pi` / `raspberry`). Change them after first boot.
- If you want to tweak image hostname, locale, or Wi‑Fi settings, edit `image/pi-gen-config` before building.
- The stage requires network access during build if your repository depends on remote packages; ensure the host has Internet connectivity.
- To customize the SSID/password, edit `config/hotspot/hostapd.conf` in the repository before building.

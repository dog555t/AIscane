# Standalone Flashable Image Builder

This folder contains everything needed to create a ready-to-boot Raspberry Pi OS image with the receipt scanner preinstalled, hotspot enabled, and services auto-starting on first boot. The image is compatible with Raspberry Pi Imager and can be distributed as a standalone OS.

## Using Pre-built Images

The easiest way to get started is to download a pre-built image from the [Releases page](https://github.com/dog555t/AIscane/releases).

### Installation with Raspberry Pi Imager (Recommended)

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Download the latest `.img.xz` file from [Releases](https://github.com/dog555t/AIscane/releases/latest)
3. In Raspberry Pi Imager:
   - Click "Choose OS" → "Use custom"
   - Select the downloaded `.img.xz` file
   - Click "Choose Storage" and select your SD card
   - Click "Write"
4. Boot your Raspberry Pi with the flashed SD card

### Command Line Installation

```bash
# Download the image
wget https://github.com/dog555t/AIscane/releases/latest/download/receipt-scanner.img.xz

# Verify checksum (optional but recommended)
wget https://github.com/dog555t/AIscane/releases/latest/download/receipt-scanner.img.xz.sha256
sha256sum -c receipt-scanner.img.xz.sha256

# Flash to SD card (replace /dev/sdX with your SD card device)
xzcat receipt-scanner.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

### First Boot

After flashing:
1. Insert SD card and power on the Raspberry Pi
2. Wait 1-2 minutes for first boot initialization
3. Connect to WiFi: SSID `Receipt-Scanner`, password `receipt1234`
4. Open browser to `http://192.168.4.1`
5. Default credentials: `pi` / `raspberry` (change immediately!)

## Building Your Own Image

### Prerequisites
- Debian/Ubuntu host (recommended: Ubuntu 22.04 or newer)
- At least 20GB free disk space
- Root/sudo access
- Internet connection for downloading packages
- Required packages:
  ```bash
  sudo apt-get install -y git rsync qemu-user-static debootstrap \
    zerofree zip dosfstools libarchive-tools xz-utils
  ```

### Automated Build (Recommended)

Use the provided build script:

```bash
cd image
./build-image.sh
```

The script will:
1. Clone or update pi-gen
2. Copy configuration files
3. Build the complete image (30-60 minutes)
4. Compress the image with xz
5. Generate SHA256 checksums

The final image will be in `pi-gen-build/deploy/receipt-scanner-*.img.xz`

#### Build Options

Environment variables you can set:

```bash
# Clean build (remove previous artifacts)
CLEAN_BUILD=1 ./build-image.sh

# Use existing pi-gen directory
PI_GEN_DIR=/path/to/pi-gen ./build-image.sh

# Specify architecture (default: arm64)
BUILD_ARCH=arm64 ./build-image.sh
```

### Manual Build

If you prefer manual control:

1. Clone pi-gen:
   ```bash
   git clone https://github.com/RPi-Distro/pi-gen.git
   cd pi-gen
   ```

2. Copy configuration:
   ```bash
   cp /path/to/AIscane/image/pi-gen-config config
   cp -r /path/to/AIscane/image/stage-receipt-scanner .
   ```

3. Build the image:
   ```bash
   export RECEIPT_SCANNER_SRC=/path/to/AIscane
   sudo env RECEIPT_SCANNER_SRC="$RECEIPT_SCANNER_SRC" ./build.sh
   ```

4. The image will be in `deploy/receipt-scanner-*.img`

## What the stage configures
- **System packages**: Python, Tesseract OCR, hostapd, dnsmasq, SQLite, and all dependencies
- **Application**: Copies repository to `/home/pi/receipt-scanner` with Python virtual environment
- **Hotspot**: Configures WiFi AP on `192.168.4.1` with SSID `Receipt-Scanner`
- **Services**: Enables systemd units for web app, battery monitor, and hotspot NAT
- **I2C**: Enables I2C interface for battery monitoring
- **First-boot**: Installs customization script for Pi Imager compatibility

## Automated Image Releases

GitHub Actions automatically builds and releases images when you push a version tag:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This triggers the build workflow which:
1. Builds the complete image using pi-gen
2. Compresses it with xz (maximum compression)
3. Generates SHA256 checksums
4. Creates a GitHub release with the image and metadata
5. Uploads release artifacts

You can also trigger a manual build from the Actions tab.

## Pi Imager Compatibility

The built image includes:
- **os_list_imagingutility.json**: Metadata for custom OS listing
- **First-boot script**: Handles Pi Imager customizations (hostname, user, WiFi, etc.)
- **Proper partitioning**: Compatible with Pi Imager's resizing

Users can apply customizations through Pi Imager's settings (Ctrl+Shift+X) before writing.

## Image Customization

Before building, you can customize:

### Network Settings
Edit `config/hotspot/hostapd.conf` to change:
- SSID (default: `Receipt-Scanner`)
- Password (default: `receipt1234`)
- WiFi channel

### Default Credentials
Edit `image/pi-gen-config`:
```
FIRST_USER_NAME=pi
FIRST_USER_PASS=raspberry
```

### Hostname and Locale
Edit `image/pi-gen-config`:
```
TARGET_HOSTNAME=receipt-scanner
TIMEZONE=Etc/UTC
LOCALE_DEFAULT=en_US.UTF-8
```

### Application Settings
Modify files in the repository before building - they will be copied into the image.

## Distribution

To distribute your custom image:

1. **Self-hosted**: Upload to your own web server
2. **GitHub Releases**: Use the automated workflow (recommended)
3. **Pi Imager JSON**: Create custom `os_list_imagingutility.json` pointing to your image URL

Example JSON for custom distribution:
```json
{
  "os_list": [{
    "name": "Receipt Scanner OS",
    "url": "https://your-server.com/receipt-scanner.img.xz",
    "extract_size": 4294967296,
    "image_download_size": 1073741824,
    "extract_sha256": "your-sha256-checksum"
  }]
}
```

## Troubleshooting

### Build fails with "out of space"
- Ensure at least 20GB free space
- Use `CLEAN_BUILD=1` to remove old artifacts
- GitHub Actions uses maximize-build-space action

### Services don't start on first boot
- Check logs: `journalctl -u receipt_scanner.service`
- Verify first-boot ran: `ls -l /var/lib/receipt-scanner-firstboot-done`
- Check service status: `systemctl status receipt_scanner`

### Hotspot not working
- Verify hostapd config: `sudo systemctl status hostapd`
- Check dnsmasq: `sudo systemctl status dnsmasq`
- Ensure WiFi isn't disabled: `rfkill list`

### Image too large
- Reduce stage inclusion (edit build script to skip unnecessary stages)
- Use minimal base image
- Remove unused packages in `stage-receipt-scanner/00-packages`

## Notes
- Default credentials match pi-gen defaults (`pi` / `raspberry`) - **change immediately after first boot**
- Build time: 30-60 minutes depending on host performance
- Final compressed image: ~1-2GB
- Requires network during build for package downloads
- First boot takes 1-2 minutes to complete initialization
- Compatible with Raspberry Pi 4 and 5 (both 32-bit and 64-bit)

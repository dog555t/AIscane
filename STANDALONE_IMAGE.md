# Receipt Scanner OS - Standalone Image

[![Download Latest Release](https://img.shields.io/github/v/release/dog555t/AIscane?label=Download%20Latest%20Image)](https://github.com/dog555t/AIscane/releases/latest)

This is a standalone, pre-configured Raspberry Pi OS image with the Receipt Scanner application fully installed and ready to use.

## What's Included

✅ **Fully Configured System**
- Raspberry Pi OS Bookworm (based on Debian 12)
- Receipt Scanner web application pre-installed
- All dependencies and services configured
- Wi-Fi hotspot automatically enabled
- Battery monitoring for UPS support

✅ **Zero Configuration Required**
- Boot and it's ready to use
- No manual installation steps
- No command line required
- Access via web browser at http://192.168.4.1

## Hardware Requirements

### Required
- **Raspberry Pi 5** (recommended) or **Raspberry Pi 4**
- **Raspberry Pi AI Camera Module** or compatible camera
- **MicroSD card** (16GB minimum, 32GB+ recommended)
- **Power supply** (official Raspberry Pi power supply recommended)

### Optional
- **MakerFocus UPS Battery Pack** (for battery monitoring and safe shutdown)

## Installation

### Option 1: Raspberry Pi Imager (Easiest)

1. **Download Raspberry Pi Imager**
   - Visit: https://www.raspberrypi.com/software/
   - Install for your operating system (Windows, macOS, Linux)

2. **Download the Image**
   - Go to: https://github.com/dog555t/AIscane/releases/latest
   - Download `receipt-scanner-*.img.xz` (typically 1-2GB)

3. **Flash the Image**
   - Open Raspberry Pi Imager
   - Click "Choose OS" → "Use custom"
   - Select the downloaded `.img.xz` file
   - Click "Choose Storage" → Select your microSD card
   - (Optional) Click gear icon ⚙️ to customize:
     - Hostname
     - Enable SSH
     - Set username/password
     - Configure WiFi (in addition to hotspot)
     - Set locale and timezone
   - Click "Write" and wait for completion

4. **Boot Your Pi**
   - Insert the flashed SD card into your Raspberry Pi
   - Connect the AI Camera Module
   - Power on the device

### Option 2: Command Line

```bash
# Download the image
wget https://github.com/dog555t/AIscane/releases/latest/download/receipt-scanner.img.xz

# Download and verify checksum (recommended)
wget https://github.com/dog555t/AIscane/releases/latest/download/receipt-scanner.img.xz.sha256
sha256sum -c receipt-scanner.img.xz.sha256

# Flash to SD card (replace /dev/sdX with your SD card device - be very careful!)
# Use 'lsblk' or 'fdisk -l' to identify your SD card
xzcat receipt-scanner.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync

# Ensure all data is written
sync
```

⚠️ **Warning**: Double-check your device name (`/dev/sdX`). Using the wrong device will destroy data!

## First Boot

1. **Initial Startup** (2-3 minutes)
   - Insert SD card into Raspberry Pi
   - Connect power
   - Wait for system to boot (LED will blink)
   - First boot runs initialization scripts

2. **Connect to Hotspot**
   - On your phone/laptop, connect to WiFi:
     - **SSID**: `Receipt-Scanner`
     - **Password**: `receipt1234`
   - You should be automatically redirected to the web interface
   - Or manually open: http://192.168.4.1

3. **Login to Web Interface**
   - Default web app credentials:
     - **Username**: `admin`
     - **Password**: `admin123`
   - ⚠️ **Change password immediately** via user menu → Change Password

4. **Start Using**
   - The dashboard loads after login
   - Click "Scan Receipt" to capture a photo
   - Or upload existing receipt images
   - View, search, and manage your receipts

## Default Credentials

**System Login** (SSH or console):
- Username: `pi`
- Password: `RaspberryPi@2024`
- ⚠️ Change immediately: `ssh pi@192.168.4.1` then run `passwd`

**Web Interface**:
- Username: `admin`
- Password: `admin123`
- ⚠️ Change immediately via user menu → Change Password

## Network Configuration

### Built-in Hotspot
- **SSID**: Receipt-Scanner
- **Password**: receipt1234
- **IP Address**: 192.168.4.1
- **DHCP Range**: 192.168.4.2 - 192.168.4.20

### Connecting to Existing WiFi
You can also connect the Pi to your existing WiFi network:

```bash
# Via SSH or console
sudo raspi-config
# Navigate to: System Options → Wireless LAN
# Enter your SSID and password
```

Or configure via Pi Imager before flashing (recommended).

When connected to WiFi, the hotspot remains active so you can use both.

## Using the Receipt Scanner

### Scanning Receipts
1. Open http://192.168.4.1 in your browser
2. Click "Scan Receipt"
3. Camera captures automatically
4. OCR extracts vendor, date, total, tax
5. Data saved to database

### Uploading Receipts
1. Click "Upload Receipt"
2. Select image file (JPG, PNG)
3. System processes and extracts data

### Managing Data
- **Dashboard**: View recent receipts
- **All Receipts**: Searchable table with sorting
- **Edit**: Click any receipt to view/edit details
- **Export**: Download all data as CSV
- **Images**: Stored in `/home/pi/receipt-scanner/data/images/`

## Accessing Data

### Via Web Interface
- Export CSV: http://192.168.4.1/export/csv

### Via File System (SSH/SFTP)
- SQLite Database: `/home/pi/receipt-scanner/data/receipts.db`
- CSV File: `/home/pi/receipt-scanner/data/receipts.csv`
- Images: `/home/pi/receipt-scanner/data/images/`
- Logs: `/var/log/receipt_scanner.log`

### Backup Your Data
```bash
# Connect via SSH
scp pi@192.168.4.1:/home/pi/receipt-scanner/data/receipts.db ./backup-receipts.db
scp -r pi@192.168.4.1:/home/pi/receipt-scanner/data/images ./backup-images/
```

## Services

The image includes several systemd services that start automatically:

| Service | Description | Command |
|---------|-------------|---------|
| `receipt_scanner.service` | Main web application | `systemctl status receipt_scanner` |
| `battery_monitor.service` | UPS battery monitoring | `systemctl status battery_monitor` |
| `hotspot_nat.service` | Hotspot NAT/iptables | `systemctl status hotspot_nat` |
| `hostapd.service` | WiFi access point | `systemctl status hostapd` |
| `dnsmasq.service` | DHCP and DNS server | `systemctl status dnsmasq` |

### Check Service Status
```bash
ssh pi@192.168.4.1
sudo systemctl status receipt_scanner
journalctl -u receipt_scanner -f  # View live logs
```

## Troubleshooting

### Can't Connect to Hotspot
1. Wait 2-3 minutes after first boot
2. Check if hotspot is visible in WiFi list
3. Verify password: `receipt1234`
4. Check service: `sudo systemctl status hostapd`
5. Restart if needed: `sudo systemctl restart hostapd dnsmasq`

### Web Interface Not Loading
1. Ensure connected to `Receipt-Scanner` WiFi
2. Try: http://192.168.4.1 or http://receipt-scanner.local
3. Check service: `sudo systemctl status receipt_scanner`
4. View logs: `journalctl -u receipt_scanner -n 50`

### Camera Not Working
1. Check camera cable connection (blue side to camera)
2. Enable camera: `sudo raspi-config` → Interface Options → Camera
3. Test: `libcamera-hello`
4. Verify in logs: `journalctl -u receipt_scanner`

### OCR Not Accurate
1. Ensure good lighting
2. Place receipt on white background
3. Avoid shadows and glare
4. Keep receipt flat
5. Edit results manually if needed

### Battery Monitor Issues
1. Check I2C is enabled: `sudo raspi-config` → Interface Options → I2C
2. Verify UPS connection: `i2cdetect -y 1`
3. Check logs: `journalctl -u battery_monitor -n 50`
4. View battery log: `cat /home/pi/receipt-scanner/data/battery.log`

## Customization

### Change Hotspot Settings
```bash
ssh pi@192.168.4.1
sudo nano /etc/hostapd/hostapd.conf
# Edit ssid= and wpa_passphrase=
sudo systemctl restart hostapd
```

### Change Web Interface Port
```bash
ssh pi@192.168.4.1
nano /home/pi/receipt-scanner/app.py
# Change port in: app.run(host='0.0.0.0', port=5000)
sudo systemctl restart receipt_scanner
```

### Update Application
```bash
ssh pi@192.168.4.1
cd /home/pi/receipt-scanner
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart receipt_scanner
```

## System Maintenance

### Update System Packages
```bash
ssh pi@192.168.4.1
sudo apt update
sudo apt upgrade -y
sudo reboot
```

### Check Disk Space
```bash
df -h
# To free space, old images can be deleted from:
# /home/pi/receipt-scanner/data/images/
```

### View System Logs
```bash
# Application logs
journalctl -u receipt_scanner -f

# Battery monitor logs
journalctl -u battery_monitor -f

# System logs
sudo dmesg | tail -50
```

## Support and Documentation

- **Full Documentation**: https://github.com/dog555t/AIscane/blob/main/README.md
- **Report Issues**: https://github.com/dog555t/AIscane/issues
- **Discussions**: https://github.com/dog555t/AIscane/discussions

## Technical Details

- **Base OS**: Raspberry Pi OS Bookworm (Debian 12)
- **Build System**: rpi-image-gen (official Raspberry Pi tool)
- **Python Version**: 3.11+
- **OCR Engine**: Tesseract 5.x
- **Database**: SQLite 3 + CSV
- **Web Framework**: Flask
- **Camera Interface**: libcamera
- **Image Generation**: YAML-based declarative config with modular layers

## License

See repository for license information.

---

**Made with ❤️ for offline receipt management**

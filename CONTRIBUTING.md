# Developer Quick Start

This guide helps developers and contributors work with the Receipt Scanner OS project.

## Project Structure

```
AIscane/
├── app.py                      # Flask web application
├── camera.py                   # Camera interface (libcamera)
├── ocr.py                      # OCR processing (Tesseract)
├── data_store.py              # SQLite/CSV storage
├── battery_monitor.py          # UPS monitoring
├── config/                     # Configuration files
│   └── hotspot/               # WiFi hotspot configs
├── services/                   # Systemd service files
├── templates/                  # HTML templates
├── image/                      # Image building tools
│   ├── build-image.sh         # Automated build script
│   ├── firstboot.sh           # First-boot customization
│   ├── os_list_imagingutility.json  # Pi Imager metadata
│   └── stage-receipt-scanner/ # Pi-gen custom stage
└── .github/workflows/         # CI/CD automation
```

## Development Setup

### Prerequisites
- Raspberry Pi OS (or compatible Linux for testing)
- Python 3.11+
- Tesseract OCR
- libcamera (for camera support)

### Local Development

```bash
# Clone the repository
git clone https://github.com/dog555t/AIscane.git
cd AIscane

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv tesseract-ocr libtesseract-dev

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the application
python app.py
```

Access the web interface at http://localhost:5000

### Testing Without Hardware

The application includes fallback modes for development without Raspberry Pi hardware:
- **Camera**: Creates placeholder images if libcamera is unavailable
- **Battery**: Logs warnings if I2C/UPS not present
- **Hotspot**: Can be disabled for development

## Building Images

### Local Build

```bash
cd image
sudo ./build-image.sh
```

Requirements:
- Ubuntu/Debian Linux host
- 20GB+ free disk space
- Root access
- Internet connection

Build time: 30-60 minutes

### CI/CD Build

Images are automatically built when version tags are pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Monitor at: https://github.com/dog555t/AIscane/actions

## Making Changes

### Code Changes

1. **Fork and clone** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make changes** following the existing code style
4. **Test thoroughly** on actual hardware if possible
5. **Commit**: Use clear, descriptive commit messages
6. **Push and create PR**

### Documentation Changes

- Update relevant `.md` files
- Keep `STANDALONE_IMAGE.md` user-focused
- Keep `image/README.md` build-focused
- Keep `RELEASE.md` maintainer-focused

### Image Configuration Changes

If you modify:
- **Hotspot settings**: Update `config/hotspot/`
- **Services**: Update `services/` and `image/stage-receipt-scanner/01-setup.sh`
- **Dependencies**: Update `requirements.txt` and `image/stage-receipt-scanner/00-packages`
- **First-boot**: Update `image/firstboot.sh`

## Testing

### Manual Testing

```bash
# Run the app
python app.py

# Test OCR
python -c "from ocr import run_ocr; print(run_ocr('path/to/receipt.jpg'))"

# Test database
python -c "from data_store import store_receipt; print('DB OK')"
```

### Hardware Testing

Test on actual Raspberry Pi:
1. Flash your built image to SD card
2. Boot and verify first boot completion
3. Connect to hotspot
4. Test web interface
5. Test camera capture
6. Test OCR processing
7. Verify service status: `systemctl status receipt_scanner`

### Integration Testing

```bash
# Check all services
sudo systemctl status receipt_scanner battery_monitor hotspot_nat hostapd dnsmasq

# View logs
journalctl -u receipt_scanner -f
journalctl -u battery_monitor -f

# Test camera
libcamera-still -o test.jpg

# Test OCR
tesseract test.jpg stdout
```

## Release Process

See [RELEASE.md](RELEASE.md) for detailed release instructions.

Quick version:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions handles the rest.

## Troubleshooting

### Build Issues

**Out of space:**
```bash
# Clean old builds
sudo rm -rf pi-gen-build/work pi-gen-build/deploy
```

**Permission errors:**
```bash
# Ensure running as root
sudo ./build-image.sh
```

**Package errors:**
- Check internet connection
- Verify package names in `image/stage-receipt-scanner/00-packages`
- Check pi-gen compatibility with current Raspberry Pi OS version

### Runtime Issues

**Camera not working:**
```bash
# Check camera connection
vcgencmd get_camera

# Test libcamera
libcamera-hello --list-cameras
```

**OCR failing:**
```bash
# Verify Tesseract
tesseract --version

# Test manually
tesseract image.jpg stdout
```

**Services not starting:**
```bash
# Check status
systemctl status receipt_scanner

# View logs
journalctl -u receipt_scanner -n 50

# Restart
sudo systemctl restart receipt_scanner
```

## Code Style

- **Python**: Follow PEP 8
- **Bash**: Use shellcheck
- **Comments**: Add only when clarifying complex logic
- **Naming**: Use descriptive names matching existing patterns

## Contributing

1. Check [Issues](https://github.com/dog555t/AIscane/issues) for existing problems
2. Fork and create a branch
3. Make focused, minimal changes
4. Test on hardware when possible
5. Update documentation
6. Submit PR with clear description

## Resources

- **pi-gen**: https://github.com/RPi-Distro/pi-gen
- **Raspberry Pi Documentation**: https://www.raspberrypi.com/documentation/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **Flask**: https://flask.palletsprojects.com/

## Support

- **Issues**: https://github.com/dog555t/AIscane/issues
- **Discussions**: https://github.com/dog555t/AIscane/discussions
- **Documentation**: See README.md and STANDALONE_IMAGE.md

---

Happy coding! 🚀

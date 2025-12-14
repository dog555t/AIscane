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
├── auth.py                     # Authentication and user management
├── config/                     # Configuration files
│   └── hotspot/               # WiFi hotspot configs
├── services/                   # Systemd service files
├── templates/                  # HTML templates
├── static/                     # Static assets (CSS, JS)
└── data/                       # Application data (created at runtime)
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

## Running the Application

The application is designed to run in any folder on your Raspberry Pi. After setting up the development environment, simply run:

```bash
python app.py
```

The web interface will be available at http://localhost:5000 (or http://192.168.4.1 when using the hotspot).

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
- Keep README.md user-focused and clear
- Document any new features or configuration options

### Configuration Changes

If you modify:
- **Hotspot settings**: Update `config/hotspot/`
- **Services**: Update `services/` systemd unit files
- **Dependencies**: Update `requirements.txt`
- **Authentication**: Update relevant sections in README.md

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
1. Clone the repository to your Raspberry Pi
2. Set up the Python environment
3. Run the application
4. Test web interface
5. Test camera capture
6. Test OCR processing
7. Verify service status: `systemctl status receipt_scanner` (if systemd services are installed)

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

To create a new release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

This tags the version in the repository.

## Troubleshooting

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

- **Raspberry Pi Documentation**: https://www.raspberrypi.com/documentation/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **Flask**: https://flask.palletsprojects.com/
- **Flask-Login**: https://flask-login.readthedocs.io/

## Support

- **Issues**: https://github.com/dog555t/AIscane/issues
- **Discussions**: https://github.com/dog555t/AIscane/discussions
- **Documentation**: See README.md

---

Happy coding! 🚀

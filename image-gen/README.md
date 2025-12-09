# Receipt Scanner OS Image Generation

This directory contains the configuration and scripts for building a standalone Receipt Scanner OS image using **rpi-image-gen**.

## What is rpi-image-gen?

[rpi-image-gen](https://github.com/raspberrypi/rpi-image-gen) is the official Raspberry Pi tool for creating custom OS images. It offers several advantages over the older pi-gen system:

- ✅ **Faster builds** - Uses pre-built packages instead of building from source
- ✅ **No root required** - Uses podman unshare for proper permissions
- ✅ **Simpler configuration** - Declarative YAML-based config files
- ✅ **Production-ready** - Same binaries used by millions worldwide
- ✅ **Modular layers** - Clean separation of concerns with validation
- ✅ **Better CI/CD** - Designed for modern automation workflows

## Prerequisites

### Install rpi-image-gen

```bash
# Clone rpi-image-gen
git clone https://github.com/raspberrypi/rpi-image-gen.git
cd rpi-image-gen

# Install dependencies
sudo ./install_deps.sh

# Add to PATH or create a symlink
export PATH="$PWD:$PATH"
# Or: sudo ln -s $PWD/rpi-image-gen /usr/local/bin/
```

### System Requirements

- Debian/Ubuntu-based Linux (Debian Bookworm or Trixie recommended)
- At least 10GB free disk space
- Regular user account (do NOT run as root)
- **Internet connection required** for:
  - Downloading Debian/Raspbian packages
  - Installing Python dependencies via pip
  - Cloning rpi-image-gen (first-time setup)
- **Network access** to:
  - `deb.debian.org` and Debian mirror repositories
  - `archive.raspberrypi.org` for Raspberry Pi specific packages
  - `pypi.org` for Python packages
  - `github.com` for rpi-image-gen

**Note**: If building behind a firewall or proxy, ensure the above domains are accessible.

## Building the Image

### Quick Build

```bash
cd image-gen
./build-image.sh
```

The script will:
1. Validate that rpi-image-gen is installed
2. Build the complete OS image (30-60 minutes on first run)
3. Compress the image with xz
4. Generate SHA256 checksums
5. Create release-ready files in `work/image-receipt-scanner/`

### Custom Build Options

```bash
# Use a different config file
CONFIG_FILE=my-custom-config.yaml ./build-image.sh

# Use a different work directory
WORK_DIR=/tmp/build-work ./build-image.sh

# Clean build (remove previous work directory first)
rm -rf work
./build-image.sh
```

## Configuration

### Main Config File

The primary configuration is in `config/receipt-scanner.yaml`:

```yaml
device:
  layer: rpi5              # Target Raspberry Pi 5
  user1: pi                # Default username
  user1pass: raspberry     # Default password

image:
  layer: image-rpios       # Use RPi OS image layout
  boot_part_size: 512M     # Boot partition size
  root_part_size: 4G       # Root partition size
  name: receipt-scanner    # Image name

layer:
  base: bookworm-desktop-min  # Minimal desktop base
  app: receipt-scanner        # Custom application layer

# Application-specific settings
receipt_scanner:
  hotspot_ssid: Receipt-Scanner
  hotspot_password: receipt1234
  web_admin_user: admin
  web_admin_pass: admin123
```

### Custom Layer

The Receipt Scanner application layer is defined in `layer/receipt-scanner.yaml`. This layer:

- Installs all required packages (Python, Tesseract, hostapd, etc.)
- Copies the application files to `/home/pi/receipt-scanner`
- Sets up Python virtual environment with dependencies
- Configures WiFi hotspot with custom SSID/password
- Installs and enables systemd services
- Enables I2C for battery monitoring
- Configures first-boot customization

## Directory Structure

```
image-gen/
├── config/
│   └── receipt-scanner.yaml    # Main build configuration
├── layer/
│   └── receipt-scanner.yaml    # Custom application layer
├── build-image.sh              # Build script
└── README.md                   # This file
```

## Customization

### Change Hotspot Settings

Edit `config/receipt-scanner.yaml`:

```yaml
receipt_scanner:
  hotspot_ssid: MyCustomSSID
  hotspot_password: MySecurePassword123
```

### Change Default User

Edit `config/receipt-scanner.yaml`:

```yaml
device:
  user1: myuser
  user1pass: mypassword
```

### Add Additional Packages

Edit `layer/receipt-scanner.yaml` and add to the packages list:

```yaml
mmdebstrap:
  packages:
    - python3
    - your-package-here
```

### Modify Installation Steps

Edit the `customize-hooks` section in `layer/receipt-scanner.yaml` to add or modify installation steps.

## Using Pre-built Images

Pre-built images are available on the [Releases page](https://github.com/dog555t/AIscane/releases).

### Installation

1. Download the latest `.img.xz` file
2. Flash it using:
   - **Raspberry Pi Imager** (recommended)
   - Command line: `xzcat receipt-scanner.img.xz | sudo dd of=/dev/sdX bs=4M status=progress`

### First Boot

1. Insert SD card and power on
2. Wait 1-2 minutes for initialization
3. Connect to WiFi "Receipt-Scanner" (password: `receipt1234`)
4. Open browser to `http://192.168.4.1`
5. Default web login: `admin` / `admin123`
6. Default OS login: `pi` / `raspberry`

⚠️ **Change both passwords immediately!**

## Automated Releases

GitHub Actions automatically builds and releases images when you push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow will:
1. Install rpi-image-gen
2. Build the complete image
3. Compress and checksum the image
4. Create a GitHub release with artifacts

## Testing the Configuration

Before running a full build, you can validate your configuration:

```bash
cd image-gen

# Check if rpi-image-gen is available
which rpi-image-gen

# Validate the config file (requires rpi-image-gen)
rpi-image-gen config -S . -c receipt-scanner.yaml --validate

# List layers used by the config
rpi-image-gen config -S . -c receipt-scanner.yaml --list-layers

# Check custom layer metadata
rpi-image-gen layer -S . --describe receipt-scanner
```

These commands help ensure your configuration is correct before starting a time-consuming build.

## Troubleshooting

### Network Connectivity Issues

If the build fails with package download errors:

```bash
# Test connectivity to Debian repositories
curl -I https://deb.debian.org/
curl -I https://archive.raspberrypi.org/

# Test connectivity to PyPI
curl -I https://pypi.org/

# If behind a proxy, set proxy environment variables
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080
```

**Common causes:**
- Firewall blocking package repositories
- Corporate proxy not configured
- DNS resolution issues
- Network timeout during large downloads

**Solutions:**
- Ensure firewall allows access to Debian, Raspbian, and PyPI repositories
- Configure proxy settings if behind a corporate firewall
- Increase timeout values in podman/mmdebstrap config if on slow connection
- Use a local package cache/mirror if available

### "rpi-image-gen not found"

Make sure rpi-image-gen is installed and in your PATH:

```bash
which rpi-image-gen
# If not found, add to PATH or create symlink
```

### "Permission denied" or root-related errors

Do NOT run as root. rpi-image-gen uses podman unshare for proper permissions:

```bash
# Run as regular user
./build-image.sh
```

### Build fails with package errors

Check your internet connection and try again. The build downloads packages from Debian/Raspbian repositories.

### "Layer not found" error

Make sure you're running the build script from the `image-gen` directory, or the source directory path is correct.

## Migration from pi-gen

This new system replaces the old pi-gen-based build in the `image/` directory. Key differences:

| Feature | pi-gen (old) | rpi-image-gen (new) |
|---------|--------------|---------------------|
| Build time | 60-90 min | 30-60 min |
| Root required | Yes | No |
| Config format | Shell scripts | YAML |
| Package source | Build from source | Pre-built packages |
| Validation | Manual | Automatic |
| Modularity | Stages | Layers |

## Support

- **Documentation**: See main [README.md](../README.md)
- **Issues**: https://github.com/dog555t/AIscane/issues
- **rpi-image-gen docs**: https://raspberrypi.github.io/rpi-image-gen/

## License

See repository root for license information.

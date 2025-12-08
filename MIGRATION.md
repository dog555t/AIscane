# Migration Guide: pi-gen to rpi-image-gen

This guide helps you migrate from the old pi-gen build system to the new rpi-image-gen system.

## Why Migrate?

The Receipt Scanner OS project has migrated from pi-gen to rpi-image-gen for significant improvements:

### Key Benefits

| Feature | pi-gen (old) | rpi-image-gen (new) |
|---------|--------------|---------------------|
| **Build Speed** | 60-90 minutes | 30-60 minutes ⚡ |
| **Root Access** | Required (sudo) | Not required 🔒 |
| **Configuration** | Shell scripts | Declarative YAML 📝 |
| **Packages** | Build from source | Pre-built binaries 🎯 |
| **Validation** | Manual | Automatic ✅ |
| **Architecture** | Stages | Modular layers 🧩 |
| **Maintenance** | Community | Official Raspberry Pi 🏢 |
| **Disk Space** | 20GB+ | 10GB+ 💾 |

### Additional Advantages

- **Production-ready**: Uses same packages as official Raspberry Pi OS
- **Better CI/CD**: Designed for automation workflows
- **Active development**: Official Raspberry Pi tool
- **Comprehensive docs**: Extensive documentation and examples
- **No containers as root**: Uses podman unshare for proper permissions

## For End Users

### Using Pre-built Images

**Nothing changes for you!** The migration is transparent:

- Download images from the same [Releases page](https://github.com/dog555t/AIscane/releases)
- Flash using Raspberry Pi Imager (same process)
- Boot and use exactly the same way
- Same features, credentials, and functionality

The only difference is images are now built faster and more reliably.

## For Developers

### Prerequisites

First, install rpi-image-gen:

```bash
# Clone rpi-image-gen
git clone https://github.com/raspberrypi/rpi-image-gen.git
cd rpi-image-gen

# Install dependencies (Debian/Ubuntu)
sudo ./install_deps.sh

# Add to PATH
export PATH="$PWD:$PATH"
# Or create a symlink
# sudo ln -s $PWD/rpi-image-gen /usr/local/bin/

# Verify installation
rpi-image-gen --help
```

### Building Locally

**Old way (deprecated):**
```bash
cd image
sudo ./build-image.sh  # Requires root, 60-90 min
```

**New way:**
```bash
cd image-gen
./build-image.sh  # No root needed, 30-60 min
```

### Configuration Changes

#### Old System (pi-gen)

Configuration was split across multiple files:

```
image/
├── pi-gen-config          # Shell variables
├── build-image.sh         # Complex build script
└── stage-receipt-scanner/
    ├── 00-packages        # Package list
    └── 01-setup.sh        # Bash installation script
```

#### New System (rpi-image-gen)

Configuration is consolidated and declarative:

```
image-gen/
├── config/
│   └── receipt-scanner.yaml    # Main config (YAML)
├── layer/
│   └── receipt-scanner.yaml    # Custom layer (YAML)
└── build-image.sh              # Simple build script
```

### Configuration Mapping

#### Basic Settings

**Old (pi-gen-config):**
```bash
IMG_NAME=receipt-scanner
TARGET_HOSTNAME=receipt-scanner
FIRST_USER_NAME=pi
FIRST_USER_PASS=raspberry
```

**New (config/receipt-scanner.yaml):**
```yaml
device:
  layer: rpi5
  user1: pi
  user1pass: raspberry

image:
  name: receipt-scanner
```

#### Package Installation

**Old (stage-receipt-scanner/00-packages):**
```
python3
python3-venv
tesseract-ocr
hostapd
dnsmasq
```

**New (layer/receipt-scanner.yaml):**
```yaml
mmdebstrap:
  packages:
    - python3
    - python3-venv
    - tesseract-ocr
    - hostapd
    - dnsmasq
```

#### Installation Scripts

**Old (stage-receipt-scanner/01-setup.sh):**
```bash
#!/bin/bash -e
install -d "${ROOTFS_DIR}/home/pi/receipt-scanner"
rsync -a "$SRC/" "${ROOTFS_DIR}/home/pi/receipt-scanner/"

on_chroot <<'EOFCHROOT'
cd /home/pi/receipt-scanner
python3 -m venv .venv
pip install -r requirements.txt
EOFCHROOT
```

**New (layer/receipt-scanner.yaml):**
```yaml
mmdebstrap:
  customize-hooks:
    - |
      set -e
      RECEIPT_HOME="/home/$IGconf_device_user1/receipt-scanner"
      install -d "$1$RECEIPT_HOME"
      rsync -a "$BDEBSTRAP_SOURCEDIR/../" "$1$RECEIPT_HOME/"
      
      chroot "$1" su - "$IGconf_device_user1" -c "
        cd $RECEIPT_HOME
        python3 -m venv .venv
        . .venv/bin/activate
        pip install -r requirements.txt
      "
```

### Custom Configuration Variables

**Old system**: Hard-coded in shell scripts

**New system**: Declared in layer metadata

```yaml
# METABEGIN
# X-Env-Var-hotspot_ssid: Receipt-Scanner
# X-Env-Var-hotspot_ssid-Desc: WiFi hotspot SSID
# X-Env-Var-hotspot_password: receipt1234
# X-Env-Var-hotspot_password-Desc: WiFi hotspot password
# METAEND
```

Then used in config:
```yaml
receipt_scanner:
  hotspot_ssid: MyCustomSSID
  hotspot_password: MyPassword123
```

### CI/CD Changes

#### Old Workflow

**File**: `.github/workflows/build-image.yml` (now disabled)

```yaml
- name: Install dependencies
  run: |
    sudo apt-get install -y git rsync qemu-user-static debootstrap ...

- name: Build image
  run: |
    cd image
    sudo env RECEIPT_SCANNER_SRC="$GITHUB_WORKSPACE" ./build-image.sh
```

#### New Workflow

**File**: `.github/workflows/build-image-rpi-gen.yml`

```yaml
- name: Install rpi-image-gen
  run: |
    git clone https://github.com/raspberrypi/rpi-image-gen.git /tmp/rpi-image-gen
    cd /tmp/rpi-image-gen
    sudo ./install_deps.sh

- name: Build image
  run: |
    cd image-gen
    WORK_DIR="${{ env.WORK_DIR }}" ./build-image.sh
    # Note: No sudo required!
```

## Migration Checklist

### For Contributors

If you've been building images locally:

- [ ] Install rpi-image-gen (see Prerequisites above)
- [ ] Update your build scripts to use `image-gen/` instead of `image/`
- [ ] Remove sudo from build commands
- [ ] Update documentation references
- [ ] Test a local build to ensure it works

### For CI/CD

If you've customized the GitHub Actions workflow:

- [ ] Review new workflow: `.github/workflows/build-image-rpi-gen.yml`
- [ ] Update any custom workflows to use rpi-image-gen
- [ ] Test workflow with a test tag
- [ ] Update secrets/variables if needed

### For Customizations

If you've customized the build:

- [ ] Convert shell script customizations to YAML layer hooks
- [ ] Move hard-coded values to config variables
- [ ] Test custom configuration with `rpi-image-gen config --validate`
- [ ] Document custom variables in layer metadata

## Troubleshooting Migration

### "rpi-image-gen: command not found"

```bash
# Make sure rpi-image-gen is in your PATH
which rpi-image-gen

# If not found, add to PATH:
export PATH="/path/to/rpi-image-gen:$PATH"

# Or install it if not yet cloned
git clone https://github.com/raspberrypi/rpi-image-gen.git
```

### "Permission denied" errors

Don't use sudo! Run as regular user:

```bash
# Wrong:
sudo ./build-image.sh

# Correct:
./build-image.sh
```

### Build fails with dependency errors

Make sure you installed rpi-image-gen dependencies:

```bash
cd /path/to/rpi-image-gen
sudo ./install_deps.sh
```

### Layer not found

Make sure you're running from the correct directory:

```bash
# Run from image-gen directory
cd image-gen
./build-image.sh
```

### Can't find old build artifacts

Old builds were in `pi-gen-build/deploy/`, new builds are in `work/`:

```bash
# Old location
ls pi-gen-build/deploy/

# New location
ls work/image-receipt-scanner/
```

## Rollback (If Needed)

If you need to temporarily use the old system:

1. The old files are still in `image/` directory
2. See `image/DEPRECATED.md` for notes
3. Old workflow saved as `.github/workflows/build-image-old-pigen.yml.disabled`

**Note**: The old system is no longer maintained and will be removed in a future release.

## Getting Help

- **New system docs**: [`image-gen/README.md`](image-gen/README.md)
- **Testing guide**: [`TESTING.md`](TESTING.md)
- **Release process**: [`RELEASE.md`](RELEASE.md)
- **rpi-image-gen docs**: https://raspberrypi.github.io/rpi-image-gen/
- **Issues**: https://github.com/dog555t/AIscane/issues

## Timeline

- **Before December 2024**: Using pi-gen
- **December 2024**: Migration to rpi-image-gen
- **Future**: Old pi-gen files will be removed

## FAQ

### Q: Do I need to reflash my SD card?

**A**: No, if you're already running an image. The migration only affects how new images are built.

### Q: Will my existing images stop working?

**A**: No, existing images continue to work. This only changes the build process.

### Q: Can I still use the old build system?

**A**: Technically yes, files are in `image/`, but it's deprecated and unsupported. Please migrate to the new system.

### Q: Are the images compatible?

**A**: Yes, images are functionally identical. Same OS, same packages, same configuration.

### Q: What if I find a bug?

**A**: Please open an issue with details about whether it's in the new build system or the resulting image.

### Q: Can I contribute to improve the build system?

**A**: Yes! Pull requests welcome. Focus improvements on the `image-gen/` directory.

---

**Last updated**: December 2024

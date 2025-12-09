# ⚠️ DEPRECATED - Old pi-gen Build System

**This directory contains the old pi-gen-based build system and is deprecated.**

## Migration Notice

The project has migrated to **rpi-image-gen** for better performance and maintainability.

### Please use the new system instead:
- **New directory**: `image-gen/`
- **New documentation**: See `image-gen/README.md`
- **New workflow**: `.github/workflows/build-image-rpi-gen.yml`

## Why Migrate?

The new rpi-image-gen system offers significant improvements:

| Feature | pi-gen (old) | rpi-image-gen (new) |
|---------|--------------|---------------------|
| Build time | 60-90 min | 30-60 min ⚡ |
| Root required | Yes (sudo) | No (podman) 🔒 |
| Config format | Shell scripts | YAML 📝 |
| Package source | Build from source | Pre-built 🎯 |
| Validation | Manual | Automatic ✅ |
| Modularity | Stages | Layers 🧩 |
| Maintenance | Community | Official Raspberry Pi 🏢 |

## Migration Guide

### For Local Builds

**Old way:**
```bash
cd image
sudo ./build-image.sh  # Requires root, slow
```

**New way:**
```bash
# First, install rpi-image-gen (one-time setup)
git clone https://github.com/raspberrypi/rpi-image-gen.git
cd rpi-image-gen
sudo ./install_deps.sh
export PATH="$PWD:$PATH"

# Then build (no root required!)
cd /path/to/AIscane/image-gen
./build-image.sh  # Run as regular user, faster
```

### For CI/CD

The new workflow is already configured:
- **Old**: `.github/workflows/build-image-old-pigen.yml.disabled` (disabled)
- **New**: `.github/workflows/build-image-rpi-gen.yml` (active)

Push a tag and the new workflow will automatically build the image.

### Configuration Changes

**Old system** used shell scripts and stages:
- `image/pi-gen-config` - Shell variable config
- `image/stage-receipt-scanner/` - Custom stage with bash scripts

**New system** uses YAML and layers:
- `image-gen/config/receipt-scanner.yaml` - Declarative YAML config
- `image-gen/layer/receipt-scanner.yaml` - Modular layer with metadata

## This Directory is Kept for Reference

These files are preserved for:
1. Understanding the old build process
2. Reference when troubleshooting existing images
3. Historical documentation

**Do not use for new builds.** The files may become outdated and are no longer maintained.

## Need Help?

- **New system docs**: `image-gen/README.md`
- **Release process**: `RELEASE.md`
- **Issues**: https://github.com/dog555t/AIscane/issues

---

**Last updated**: December 2024

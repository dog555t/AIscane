# Release Process

This document describes how to create and publish new releases of the Receipt Scanner OS image.

## Automated Releases (Recommended)

The easiest way to create a release is using GitHub Actions:

### 1. Create a Version Tag

```bash
# Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. Wait for Build

The GitHub Actions workflow will automatically:
1. Build the complete OS image using pi-gen (60-90 minutes)
2. Compress the image with xz
3. Calculate SHA256 checksums
4. Create a GitHub Release
5. Upload the image and checksums as release assets

Monitor progress at: https://github.com/dog555t/AIscane/actions

### 3. Verify Release

Once complete, check:
- Release appears at: https://github.com/dog555t/AIscane/releases
- Image file is present: `receipt-scanner-*.img.xz`
- Checksums are included: `*.sha256` and `SHA256SUM`
- Release notes are populated

### 4. Update Documentation (if needed)

If you added new features, update:
- `README.md` - Quick start guide
- `STANDALONE_IMAGE.md` - User documentation
- Release notes on GitHub

## Manual Releases

If you need to build locally:

### 1. Build the Image

```bash
cd image
./build-image.sh
```

This takes 30-60 minutes depending on your machine.

### 2. Test the Image

Before releasing, test the built image:

```bash
# Flash to a test SD card
xzcat pi-gen-build/deploy/receipt-scanner*.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# Boot and verify:
# - System boots successfully
# - Hotspot is available (Receipt-Scanner)
# - Web interface loads at http://192.168.4.1
# - Camera capture works
# - OCR processing works
# - Services start automatically
```

### 3. Create Release on GitHub

1. Go to: https://github.com/dog555t/AIscane/releases/new
2. Create a new tag: `v1.0.0`
3. Set release title: `Receipt Scanner OS v1.0.0`
4. Add release notes (see template below)
5. Upload files:
   - `receipt-scanner-*.img.xz`
   - `receipt-scanner-*.img.xz.sha256`
   - `SHA256SUM`
6. Publish release

## Release Notes Template

```markdown
# Receipt Scanner OS v1.0.0

## What's New
- [List new features]
- [List improvements]
- [List bug fixes]

## Installation

Download the image and flash it using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

See [STANDALONE_IMAGE.md](https://github.com/dog555t/AIscane/blob/main/STANDALONE_IMAGE.md) for complete installation and usage instructions.

## Compatible Hardware
- Raspberry Pi 5 (recommended)
- Raspberry Pi 4
- Raspberry Pi AI Camera Module

## Quick Start
1. Flash image to SD card
2. Boot Raspberry Pi
3. Connect to WiFi: SSID `Receipt-Scanner`, password `receipt1234`
4. Open browser: http://192.168.4.1

Default credentials: `pi` / `raspberry` (⚠️ change immediately!)

## Image Details
- **Size**: [X]MB compressed
- **Base OS**: Raspberry Pi OS Bookworm
- **Build Date**: [YYYY-MM-DD]
- **SHA256**: [checksum]

## Support
- Documentation: https://github.com/dog555t/AIscane/blob/main/README.md
- Issues: https://github.com/dog555t/AIscane/issues
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major (1.0.0)**: Breaking changes, major new features
- **Minor (1.1.0)**: New features, backwards compatible
- **Patch (1.0.1)**: Bug fixes, minor improvements

## Pre-release Testing Checklist

Before releasing, verify:

### Build
- [ ] Image builds successfully without errors
- [ ] Image size is reasonable (< 2GB compressed)
- [ ] Checksums are generated correctly

### First Boot
- [ ] System boots within 2-3 minutes
- [ ] First-boot script completes successfully
- [ ] All services start automatically
- [ ] No errors in system logs

### Network
- [ ] Hotspot is available (SSID: Receipt-Scanner)
- [ ] Can connect to hotspot with password
- [ ] Gets IP via DHCP (192.168.4.x)
- [ ] DNS redirects to web interface

### Web Interface
- [ ] Loads at http://192.168.4.1
- [ ] Dashboard displays correctly
- [ ] All pages are accessible
- [ ] No console errors in browser

### Functionality
- [ ] Camera capture works
- [ ] Image upload works
- [ ] OCR processing works
- [ ] Data saves to database
- [ ] Export CSV works
- [ ] Search and filter work

### Services
- [ ] receipt_scanner.service is running
- [ ] battery_monitor.service is running (if UPS present)
- [ ] hotspot_nat.service is running
- [ ] hostapd.service is running
- [ ] dnsmasq.service is running

### Documentation
- [ ] README.md is up to date
- [ ] STANDALONE_IMAGE.md matches current features
- [ ] Release notes are accurate
- [ ] Links work correctly

## Hotfix Releases

For urgent bug fixes:

1. Create a branch from the tag:
   ```bash
   git checkout -b hotfix/v1.0.1 v1.0.0
   ```

2. Make minimal fixes

3. Test thoroughly

4. Create new tag:
   ```bash
   git tag -a v1.0.1 -m "Hotfix release 1.0.1"
   git push origin v1.0.1
   ```

5. Merge fixes back to main:
   ```bash
   git checkout main
   git merge hotfix/v1.0.1
   git push origin main
   ```

## Troubleshooting Build Issues

### Out of Disk Space
- GitHub Actions uses `maximize-build-space` action
- Local builds need 20GB+ free space
- Clean old builds: `sudo rm -rf pi-gen-build/work pi-gen-build/deploy`

### Build Hangs
- Check for interactive prompts in package installation
- Review logs in `pi-gen-build/work/*/build.log`
- Ensure DEBIAN_FRONTEND=noninteractive is set

### Image Won't Boot
- Verify image integrity with checksum
- Try reflashing SD card
- Check SD card isn't corrupted
- Use official Raspberry Pi power supply

## Support

For issues with the release process:
- Check GitHub Actions logs
- Review pi-gen documentation: https://github.com/RPi-Distro/pi-gen
- Open an issue: https://github.com/dog555t/AIscane/issues

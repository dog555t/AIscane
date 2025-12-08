# Release Process

This document describes how to create and publish new releases of the Receipt Scanner OS image.

## Recent Improvements (rpi-image-gen Migration)

The release workflow has been migrated to use **rpi-image-gen** with the following improvements:
- ✅ **Faster builds** - 30-60 minutes instead of 60-90 minutes (uses pre-built packages)
- ✅ **No root required** - Uses podman unshare instead of sudo for proper permissions
- ✅ **Simpler configuration** - Declarative YAML-based config instead of complex shell scripts
- ✅ **Production-ready** - Same binaries used by millions in Raspberry Pi OS
- ✅ **Better modularity** - Clean separation with custom layers and validation
- ✅ **Improved reliability** - Official Raspberry Pi tool with active development
- ✅ Creates both timestamped and simple filenames (`receipt-scanner.img.xz`) for stable download URLs
- ✅ Comprehensive release notes include both OS and web app credentials
- ✅ SHA256 checksums for all image files
- ✅ Supports both tag-triggered and manual workflow dispatch releases

## Automated Releases (Recommended)

The easiest way to create a release is using GitHub Actions. There are two methods:

### Method 1: Create a Version Tag (Recommended for production releases)

```bash
# Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# Create and push a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Method 2: Manual Workflow Dispatch (For testing or ad-hoc builds)

1. Go to: https://github.com/dog555t/AIscane/actions/workflows/build-image-rpi-gen.yml
2. Click "Run workflow" button
3. Optionally enter a release tag (or leave as "latest")
4. Click "Run workflow" to start the build

### Wait for Build

The GitHub Actions workflow will automatically:
1. Install rpi-image-gen and dependencies
2. Build the complete OS image using rpi-image-gen (30-60 minutes)
3. Compress the image with xz
4. Calculate SHA256 checksums
5. Create a GitHub Release (if using a version tag)
6. Upload the image and checksums as release assets

Monitor progress at: https://github.com/dog555t/AIscane/actions

### Verify Release

Once complete, check:
- Release appears at: https://github.com/dog555t/AIscane/releases
- Image files are present: `receipt-scanner-*.img.xz` and `receipt-scanner.img.xz`
- Checksums are included: `*.sha256` and `SHA256SUM`
- Release notes are populated with installation instructions

### Update Documentation (if needed)

If you added new features, update:
- `README.md` - Quick start guide
- `STANDALONE_IMAGE.md` - User documentation
- Release notes on GitHub

## Manual Releases

If you need to build locally:

### Prerequisites

First, install rpi-image-gen:

```bash
# Clone rpi-image-gen
git clone https://github.com/raspberrypi/rpi-image-gen.git
cd rpi-image-gen

# Install dependencies
sudo ./install_deps.sh

# Add to PATH
export PATH="$PWD:$PATH"
```

### 1. Build the Image

```bash
cd image-gen
./build-image.sh
```

This takes 30-60 minutes depending on your machine (faster than the old pi-gen system).

**Note:** Run as a regular user, NOT as root. rpi-image-gen uses podman unshare for proper permissions.

### 2. Test the Image

Before releasing, test the built image:

```bash
# Find the built image in work directory
IMAGE_FILE=$(find work -name "receipt-scanner*.img.xz" | head -1)

# Flash to a test SD card
xzcat "$IMAGE_FILE" | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync

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
- Local builds need 10GB+ free space (less than old pi-gen system)
- Clean old builds: `rm -rf work`

### "rpi-image-gen not found"
- Make sure rpi-image-gen is installed and in your PATH
- See manual build prerequisites above

### Permission denied or root-related errors
- Do NOT run build script as root
- rpi-image-gen uses podman unshare for proper permissions
- Run as a regular user: `./build-image.sh`

### Build fails with package download errors
- Check your internet connection
- Verify you can access Debian/Raspbian repositories
- Try again after a few minutes

### Image Won't Boot
- Verify image integrity with checksum
- Try reflashing SD card
- Check SD card isn't corrupted
- Use official Raspberry Pi power supply

### GitHub Actions Workflow Issues
- Ensure repository has write permissions for `contents` (set in workflow)
- Check that `GITHUB_TOKEN` is available (automatic in GitHub Actions)
- Build requires ~30-60 minutes (faster than old pi-gen)
- If build times out, increase timeout-minutes in the workflow

## Workflow Technical Details

The GitHub Actions workflow (`.github/workflows/build-image-rpi-gen.yml`):
- Runs on: `ubuntu-latest` with 120-minute timeout (reduced from 180 minutes)
- Build System: Uses rpi-image-gen instead of pi-gen
- Permissions: No root required (uses podman unshare)
- Environment: Uses `WORK_DIR` for build artifacts
- Output: Creates compressed `.img.xz` files with SHA256 checksums
- Release: Automatically creates GitHub release when triggered by version tag

### Key Steps:
1. Maximize build space (removes unused packages)
2. Install rpi-image-gen and dependencies
3. Build image with rpi-image-gen (as regular user)
4. Prepare release artifacts and notes
5. Create GitHub release with image files

### Migration from pi-gen

The new system offers several advantages:

| Feature | pi-gen (old) | rpi-image-gen (new) |
|---------|--------------|---------------------|
| Build time | 60-90 min | 30-60 min |
| Root required | Yes (sudo) | No (podman) |
| Config format | Shell scripts | YAML |
| Package source | Source builds | Pre-built |
| Validation | Manual | Automatic |
| Modularity | Stages | Layers |
| Maintenance | Community | Official Raspberry Pi |

## Support

For issues with the release process:
- Check GitHub Actions logs: https://github.com/dog555t/AIscane/actions
- Review rpi-image-gen documentation: https://raspberrypi.github.io/rpi-image-gen/
- Review local documentation: `image-gen/README.md`
- Open an issue: https://github.com/dog555t/AIscane/issues

# Testing Guide for Receipt Scanner OS Image

This document describes how to test the rpi-image-gen build configuration and the resulting images.

## Configuration Testing

### 1. Validate Configuration Files

Before building, validate your configuration:

```bash
cd image-gen

# Validate the main config file
rpi-image-gen config -S . -c receipt-scanner.yaml --validate

# List all layers that will be used
rpi-image-gen config -S . -c receipt-scanner.yaml --list-layers
```

Expected output should show no validation errors and list layers including:
- Base system layers (bookworm-desktop-min)
- Device layer (rpi5)
- Image layout layer (image-rpios)
- Custom application layer (receipt-scanner)

### 2. Check Custom Layer

Verify the custom layer is properly formatted:

```bash
# Show layer metadata
rpi-image-gen layer -S . --describe receipt-scanner

# Check for syntax errors in YAML
python3 -c "import yaml; yaml.safe_load(open('layer/receipt-scanner.yaml'))"
```

The layer should show:
- Name: receipt-scanner
- Category: app
- Required dependencies
- Configuration variables with defaults

### 3. Dry Run Validation

Test the build configuration without actually building:

```bash
# Note: rpi-image-gen doesn't have a --dry-run flag, but you can test package resolution
# by building just the filesystem without creating an image (advanced)
```

## Build Testing

### Prerequisites Check

Before building, verify system prerequisites:

```bash
# Check network connectivity (required for package downloads)
curl -I https://deb.debian.org/
curl -I https://archive.raspberrypi.org/
curl -I https://pypi.org/

# If behind a firewall or proxy, configure proxy settings
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080

# Verify rpi-image-gen is installed
which rpi-image-gen

# Check available disk space (need 10GB+)
df -h .
```

**Important**: The build requires unrestricted network access to:
- Debian/Raspbian package repositories (`deb.debian.org`, `archive.raspberrypi.org`)
- Python Package Index (`pypi.org`)
- GitHub for rpi-image-gen (`github.com`)

If you recently removed firewall restrictions, the build script will verify connectivity before proceeding.

### Local Build Test

Perform a test build on a local machine:

```bash
cd image-gen

# Run the build script (includes automatic network check)
./build-image.sh

# Monitor the build process
# - Should complete in 30-60 minutes
# - Check for any error messages
# - Verify no permission errors (should not require sudo)
# - Watch for package download progress
```

### Verify Build Artifacts

After a successful build:

```bash
# Find the work directory
ls -lh work/

# Check the image directory
ls -lh work/image-receipt-scanner/

# Expected files:
# - receipt-scanner-*.img.xz (compressed image)
# - receipt-scanner.img.xz (stable name copy)
# - *.sha256 (checksums)
# - SHA256SUM (combined checksums)
```

### Verify Checksums

```bash
cd work/image-receipt-scanner/

# Verify checksum integrity
sha256sum -c receipt-scanner.img.xz.sha256

# Should output: receipt-scanner.img.xz: OK
```

## Image Testing

### 1. Flash the Image

Flash to a test SD card:

```bash
# Using command line
xzcat work/image-receipt-scanner/receipt-scanner.img.xz | \
    sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
sync

# Or use Raspberry Pi Imager (recommended for testing)
# - Choose "Use custom"
# - Select the .img.xz file
# - Flash to SD card
```

### 2. First Boot Test

Insert SD card and power on the Raspberry Pi:

**Timing:**
- [ ] System boots within 2-3 minutes
- [ ] First-boot script completes (check with `ls /var/lib/receipt-scanner-firstboot-done`)
- [ ] All services start automatically

**Network:**
- [ ] WiFi hotspot is available (SSID: Receipt-Scanner)
- [ ] Can connect with password: receipt1234
- [ ] Gets IP via DHCP (192.168.4.x range)
- [ ] Gateway is accessible at 192.168.4.1

### 3. Service Status Check

SSH into the system (from a device connected to the hotspot):

```bash
ssh pi@192.168.4.1
# Password: raspberry

# Check all services are running
systemctl status receipt_scanner.service
systemctl status battery_monitor.service
systemctl status hotspot_nat.service
systemctl status hostapd.service
systemctl status dnsmasq.service

# All should show "active (running)" status
```

### 4. Web Interface Test

**Access:**
- [ ] Open browser to http://192.168.4.1
- [ ] Login page loads correctly
- [ ] Can login with admin/admin123
- [ ] Dashboard displays properly

**Functionality:**
- [ ] Can navigate to all pages (Dashboard, Scan, Upload, All Receipts)
- [ ] No JavaScript errors in browser console
- [ ] All static assets load correctly

### 5. Camera Test

Test camera capture:

```bash
# SSH into the system
ssh pi@192.168.4.1

# Test camera directly
libcamera-hello --list-cameras
# Should list the AI Camera

# Test still capture
libcamera-still -o /tmp/test.jpg
ls -lh /tmp/test.jpg
# Should create a JPEG file
```

**Web interface camera test:**
- [ ] Click "Scan Receipt" button
- [ ] Camera captures image
- [ ] Image appears in interface
- [ ] Image saved to data/images/

### 6. OCR Test

Test OCR processing:

**Prepare test receipt:**
- Create or use a test receipt image with clear text
- Should include: vendor name, date, total amount, tax

**Test via web interface:**
- [ ] Upload test receipt via "Upload Receipt"
- [ ] OCR processing completes (may take 10-30 seconds)
- [ ] Extracted fields are populated (vendor, date, total, tax)
- [ ] Data saved to database
- [ ] Can view receipt in "All Receipts"

**Test via SSH:**
```bash
ssh pi@192.168.4.1
cd receipt-scanner
source .venv/bin/activate

# Test Tesseract directly
tesseract --version
# Should show Tesseract 5.x

# Test Python OCR
python3 -c "from ocr import extract_receipt_data; print('OCR module imports OK')"
```

### 7. Database Test

Verify database operations:

```bash
ssh pi@192.168.4.1
cd receipt-scanner/data

# Check database exists and has schema
sqlite3 receipts.db ".schema"
# Should show receipts table schema

# Check if data was saved
sqlite3 receipts.db "SELECT COUNT(*) FROM receipts;"
# Should show count of receipts

# Export CSV
sqlite3 receipts.db -csv -header "SELECT * FROM receipts;" > test_export.csv
cat test_export.csv
```

**Test via web interface:**
- [ ] Navigate to export page
- [ ] Download CSV export
- [ ] CSV contains all receipt data
- [ ] CSV format is correct

### 8. Battery Monitor Test (Optional)

If using a UPS:

```bash
ssh pi@192.168.4.1

# Check battery monitor service
systemctl status battery_monitor.service
# Should be active

# Check I2C is enabled
i2cdetect -y 1
# Should show I2C devices if UPS is connected

# Check battery log
tail -20 data/battery.log
# Should show battery status updates
```

### 9. System Resource Check

Verify system resources:

```bash
ssh pi@192.168.4.1

# Check disk usage
df -h
# Root partition should have reasonable free space

# Check memory
free -h
# Should have available memory

# Check CPU temperature
vcgencmd measure_temp
# Should be < 80°C under normal operation

# Check for errors in system logs
journalctl -p err -n 50
# Should have minimal errors
```

## CI/CD Testing

### GitHub Actions Test

Test the automated workflow:

1. **Create a test tag locally:**
   ```bash
   git tag -a test-v0.0.1 -m "Test build"
   ```

2. **Push to a test branch first (optional):**
   ```bash
   git push origin copilot/revamp-imager-release-system
   ```

3. **Monitor the workflow:**
   - Go to: https://github.com/dog555t/AIscane/actions
   - Watch the build progress
   - Check for errors in each step

4. **Expected workflow results:**
   - [ ] Workflow completes in ~30-60 minutes
   - [ ] No permission errors
   - [ ] Image artifacts are created
   - [ ] Checksums are generated
   - [ ] (If tag pushed) GitHub release is created

5. **Verify artifacts:**
   - Download artifacts from workflow
   - Verify checksums
   - Test flash the image

### Cleanup Test Tags

```bash
# Delete local test tag
git tag -d test-v0.0.1

# If pushed, delete remote test tag
git push --delete origin test-v0.0.1
```

## Performance Benchmarks

Compare with old pi-gen system:

| Metric | pi-gen (old) | rpi-image-gen (new) | Improvement |
|--------|--------------|---------------------|-------------|
| Build time | 60-90 min | 30-60 min | ~40% faster |
| Disk usage | 20GB+ | 10GB+ | 50% less |
| Root required | Yes | No | Security ✓ |
| Config complexity | High | Low | Simpler ✓ |
| First boot | 2-3 min | 2-3 min | Same |
| Image size | 1-2GB | 1-2GB | Similar |

## Regression Testing Checklist

When testing a new build, verify these don't break:

**System:**
- [ ] Boots successfully
- [ ] First-boot customization runs
- [ ] Services start automatically
- [ ] No filesystem corruption

**Network:**
- [ ] Hotspot starts automatically
- [ ] DHCP assigns IPs correctly
- [ ] DNS resolution works
- [ ] NAT/forwarding works
- [ ] Can access external network (if WiFi also configured)

**Application:**
- [ ] Web server starts
- [ ] Can login to web interface
- [ ] All pages load correctly
- [ ] Camera capture works
- [ ] Image upload works
- [ ] OCR processing works
- [ ] Database operations work
- [ ] CSV export works

**Services:**
- [ ] receipt_scanner.service running
- [ ] battery_monitor.service running
- [ ] hotspot_nat.service running
- [ ] hostapd.service running
- [ ] dnsmasq.service running

## Known Issues & Limitations

Document any known issues discovered during testing:

1. **First Boot Timing**: First boot may take 2-3 minutes; users should wait patiently
2. **OCR Accuracy**: Depends on image quality, lighting, and receipt format
3. **Battery Monitor**: Only works with compatible UPS hardware
4. **Camera Support**: Requires Raspberry Pi AI Camera Module or compatible camera

## Automated Testing (Future)

Ideas for future automated testing:

- Unit tests for build configuration validation
- Integration tests for image functionality
- Automated image testing in QEMU
- CI/CD smoke tests after build
- Performance regression tests

## Support & Issues

If you discover issues during testing:

1. Check logs: `journalctl -xe`
2. Review service status: `systemctl status <service>`
3. Check build logs in GitHub Actions
4. Open an issue: https://github.com/dog555t/AIscane/issues

Include:
- Build method (local or CI/CD)
- Error messages or logs
- Steps to reproduce
- Expected vs actual behavior

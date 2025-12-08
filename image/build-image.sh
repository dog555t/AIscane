#!/bin/bash
# Build script for creating a standalone Receipt Scanner OS image using pi-gen
# This script automates the entire image building process

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PI_GEN_DIR="${PI_GEN_DIR:-${PROJECT_ROOT}/pi-gen-build}"
IMAGE_NAME="receipt-scanner"
BUILD_ARCH="${BUILD_ARCH:-arm64}"

echo "========================================="
echo "Receipt Scanner OS Image Builder"
echo "========================================="
echo "Project root: $PROJECT_ROOT"
echo "Pi-gen directory: $PI_GEN_DIR"
echo "Build architecture: $BUILD_ARCH"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "This script should NOT be run as root. It will use sudo when needed."
  exit 1
fi

# Check dependencies
echo "Checking dependencies..."
MISSING_DEPS=()
for cmd in git rsync qemu-arm-static qemu-aarch64-static debootstrap; do
  if ! command -v "$cmd" &> /dev/null; then
    MISSING_DEPS+=("$cmd")
  fi
done

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
  echo "ERROR: Missing required dependencies: ${MISSING_DEPS[*]}"
  echo ""
  echo "Please install them with:"
  echo "  sudo apt-get install -y git rsync qemu-user-static debootstrap"
  exit 1
fi

# Clone or update pi-gen
if [ ! -d "$PI_GEN_DIR" ]; then
  echo "Cloning pi-gen..."
  git clone --depth 1 https://github.com/RPi-Distro/pi-gen.git "$PI_GEN_DIR"
else
  echo "Updating pi-gen..."
  cd "$PI_GEN_DIR"
  git fetch origin
  git reset --hard origin/master
  cd - > /dev/null
fi

# Copy configuration and stage
echo "Copying configuration files..."
cp "$SCRIPT_DIR/pi-gen-config" "$PI_GEN_DIR/config"

# Copy custom stage
if [ -d "$PI_GEN_DIR/stage-receipt-scanner" ]; then
  rm -rf "$PI_GEN_DIR/stage-receipt-scanner"
fi
cp -r "$SCRIPT_DIR/stage-receipt-scanner" "$PI_GEN_DIR/"

# Create skip files to optimize build (skip stages we don't need)
# We want stage0-stage2 (base system) and our custom stage
echo "Configuring stages..."
cd "$PI_GEN_DIR"
touch stage3/SKIP stage4/SKIP stage5/SKIP
touch stage3/SKIP_IMAGES stage4/SKIP_IMAGES stage5/SKIP_IMAGES

# Clean previous builds if requested
if [ "$CLEAN_BUILD" = "1" ]; then
  echo "Cleaning previous build artifacts..."
  sudo rm -rf work deploy
fi

# Build the image
echo ""
echo "========================================="
echo "Starting image build..."
echo "This may take 30-60 minutes..."
echo "========================================="
echo ""

export RECEIPT_SCANNER_SRC="$PROJECT_ROOT"

# Run the build
sudo env RECEIPT_SCANNER_SRC="$RECEIPT_SCANNER_SRC" ./build.sh

# Check if build succeeded
if [ ! -d "deploy" ] || [ -z "$(ls -A deploy/*.img* 2>/dev/null)" ]; then
  echo ""
  echo "ERROR: Build failed - no image found in deploy directory"
  exit 1
fi

# Compress the image if not already compressed
echo ""
echo "Checking for image compression..."
IMG_FILE=$(ls deploy/${IMAGE_NAME}*.img 2>/dev/null | head -1 || true)

if [ -n "$IMG_FILE" ]; then
  echo "Compressing image with xz..."
  xz -9 -T 0 "$IMG_FILE"
  IMG_FILE="${IMG_FILE}.xz"
fi

# Calculate SHA256
if [ -z "$IMG_FILE" ]; then
  IMG_FILE=$(ls deploy/${IMAGE_NAME}*.img.xz 2>/dev/null | head -1 || true)
fi

if [ -n "$IMG_FILE" ]; then
  echo ""
  echo "Calculating SHA256 checksum..."
  sha256sum "$IMG_FILE" | tee "deploy/SHA256SUM"
  
  # Get file size
  FILE_SIZE=$(stat -c%s "$IMG_FILE")
  FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))
  
  echo ""
  echo "========================================="
  echo "Build completed successfully!"
  echo "========================================="
  echo "Image location: $IMG_FILE"
  echo "Image size: ${FILE_SIZE_MB}MB"
  echo "SHA256: $(sha256sum "$IMG_FILE" | cut -d' ' -f1)"
  echo ""
  echo "To flash the image:"
  echo "  1. Use Raspberry Pi Imager"
  echo "  2. Or use: xzcat $IMG_FILE | sudo dd of=/dev/sdX bs=4M status=progress"
  echo ""
else
  echo "ERROR: Could not find built image file"
  exit 1
fi

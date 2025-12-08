#!/bin/bash
# Build script for creating Receipt Scanner OS image using rpi-image-gen
# This is a simplified build system that replaces the complex pi-gen setup

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="receipt-scanner"
CONFIG_FILE="${CONFIG_FILE:-receipt-scanner.yaml}"
WORK_DIR="${WORK_DIR:-${PROJECT_ROOT}/work}"

echo "========================================="
echo "Receipt Scanner OS Image Builder"
echo "Using rpi-image-gen"
echo "========================================="
echo "Project root: $PROJECT_ROOT"
echo "Config file: $CONFIG_FILE"
echo "Work directory: $WORK_DIR"
echo ""

# Check if rpi-image-gen is installed
if ! command -v rpi-image-gen &> /dev/null; then
    echo "ERROR: rpi-image-gen is not installed"
    echo ""
    echo "Install it with:"
    echo "  git clone https://github.com/raspberrypi/rpi-image-gen.git"
    echo "  cd rpi-image-gen"
    echo "  sudo ./install_deps.sh"
    echo "  export PATH=\"\$PWD:\$PATH\""
    echo ""
    exit 1
fi

# Check if running with proper permissions
if [ "$(id -u)" -eq 0 ]; then
    echo "WARNING: Do not run this script as root!"
    echo "rpi-image-gen uses podman unshare and should run as a regular user."
    exit 1
fi

# Create work directory if it doesn't exist
mkdir -p "$WORK_DIR"

echo "Starting image build..."
echo "This may take 30-60 minutes on first run..."
echo ""

# Build the image
# -S sets the source directory for custom layers and configs
# -c specifies the config file
# -W sets the work directory
rpi-image-gen build \
    -S "$SCRIPT_DIR" \
    -c "$CONFIG_FILE" \
    -W "$WORK_DIR"

# Find the built image
IMAGE_DIR="$WORK_DIR/image-${IMAGE_NAME}"
if [ ! -d "$IMAGE_DIR" ]; then
    echo "ERROR: Build failed - image directory not found"
    exit 1
fi

IMAGE_FILE=$(find "$IMAGE_DIR" -name "*.img" | head -1)
if [ -z "$IMAGE_FILE" ]; then
    echo "ERROR: Build failed - no image file found"
    exit 1
fi

# Compress the image if not already compressed
echo ""
echo "Compressing image..."
if [ ! -f "${IMAGE_FILE}.xz" ]; then
    xz -9 -T 0 "$IMAGE_FILE"
    IMAGE_FILE="${IMAGE_FILE}.xz"
else
    IMAGE_FILE="${IMAGE_FILE}.xz"
fi

# Calculate checksums
echo "Calculating checksums..."
cd "$(dirname "$IMAGE_FILE")"
sha256sum "$(basename "$IMAGE_FILE")" > "$(basename "$IMAGE_FILE").sha256"

# Create a copy with consistent name for releases
SIMPLE_NAME="${IMAGE_NAME}.img.xz"
if [ "$(basename "$IMAGE_FILE")" != "$SIMPLE_NAME" ]; then
    cp "$IMAGE_FILE" "$SIMPLE_NAME"
    sha256sum "$SIMPLE_NAME" > "${SIMPLE_NAME}.sha256"
fi

# Create SHA256SUM file with all checksums
sha256sum *.img.xz > SHA256SUM 2>/dev/null || true

# Get file size (portable approach - try both Linux and macOS stat)
if stat -c%s "$IMAGE_FILE" >/dev/null 2>&1; then
    # Linux stat
    FILE_SIZE=$(stat -c%s "$IMAGE_FILE")
elif stat -f%z "$IMAGE_FILE" >/dev/null 2>&1; then
    # macOS/BSD stat
    FILE_SIZE=$(stat -f%z "$IMAGE_FILE")
else
    # Fallback: parse ls -l output
    FILE_SIZE=$(ls -l "$IMAGE_FILE" | awk '{print $5}')
fi
FILE_SIZE_MB=$((FILE_SIZE / 1024 / 1024))

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo "Image location: $IMAGE_FILE"
echo "Image size: ${FILE_SIZE_MB}MB"
echo "SHA256: $(sha256sum "$IMAGE_FILE" | cut -d' ' -f1)"
echo ""
echo "To flash the image:"
echo "  1. Use Raspberry Pi Imager"
echo "  2. Or use: xzcat $IMAGE_FILE | sudo dd of=/dev/sdX bs=4M status=progress"
echo ""

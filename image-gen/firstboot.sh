#!/bin/bash
# First-boot customization script for Receipt Scanner OS
# This script is called by Raspberry Pi OS on first boot to apply user customizations
# from the Raspberry Pi Imager

set -e

FIRST_BOOT_LOG="/var/log/receipt-scanner-first-boot.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$FIRST_BOOT_LOG"
}

log "Starting Receipt Scanner OS first boot customization..."

# Apply any Pi Imager customizations (handled by Pi OS automatically)
# This includes:
# - User creation/password
# - Hostname
# - WiFi credentials
# - SSH settings
# - Locale/timezone

# Ensure receipt scanner data directories exist with correct permissions
if [ -d /home/pi/receipt-scanner ]; then
  log "Setting up receipt scanner directories..."
  mkdir -p /home/pi/receipt-scanner/data/images
  mkdir -p /home/pi/receipt-scanner/data/exports
  chown -R pi:pi /home/pi/receipt-scanner/data
  
  # Create initial database if it doesn't exist
  if [ ! -f /home/pi/receipt-scanner/data/receipts.db ]; then
    log "Initializing database..."
    cd /home/pi/receipt-scanner
    sudo -u pi /home/pi/receipt-scanner/.venv/bin/python3 - << 'EOFPY'
import sqlite3
import os

db_path = '/home/pi/receipt-scanner/data/receipts.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
  CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    date TEXT,
    vendor TEXT,
    total TEXT,
    tax TEXT,
    image_path TEXT,
    raw_text TEXT
  )
""")
conn.commit()
conn.close()
print("Database initialized")
EOFPY
  fi
fi

# Restart services to ensure everything is running
log "Starting receipt scanner services..."
systemctl restart receipt_scanner.service || log "Warning: Failed to start receipt_scanner service"
systemctl restart battery_monitor.service || log "Warning: Failed to start battery_monitor service"
systemctl restart hotspot_nat.service || log "Warning: Failed to start hotspot_nat service"

log "First boot customization completed successfully!"
log "Receipt Scanner web interface will be available at http://192.168.4.1"
log "Connect to WiFi: SSID=Receipt-Scanner, Password=receipt1234"

exit 0

#!/bin/bash -e

if [ -z "${ROOTFS_DIR}" ]; then
  echo "ROOTFS_DIR is not set; this script must run inside pi-gen" >&2
  exit 1
fi

SRC="${RECEIPT_SCANNER_SRC:-}"
if [ -z "$SRC" ] || [ ! -d "$SRC" ]; then
  echo "Set RECEIPT_SCANNER_SRC to the absolute path of this repository before running pi-gen." >&2
  exit 1
fi

install -d "${ROOTFS_DIR}/home/pi/receipt-scanner"
rsync -a --delete --exclude '.git' --exclude '__pycache__' --exclude '.venv' "$SRC/" "${ROOTFS_DIR}/home/pi/receipt-scanner/"

# Copy hotspot iptables helper into a root-owned path used by the NAT service.
install -D -m 755 "${ROOTFS_DIR}/home/pi/receipt-scanner/config/hotspot/iptables.sh" "${ROOTFS_DIR}/usr/local/sbin/receipt-iptables.sh"

on_chroot <<'EOFCHROOT'
set -e
id -u pi >/dev/null 2>&1 || useradd -m -s /bin/bash pi
chown -R pi:pi /home/pi/receipt-scanner
mkdir -p /home/pi/receipt-scanner/data/images /home/pi/receipt-scanner/data/exports

cd /home/pi/receipt-scanner
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Deploy hotspot configs
install -d /etc/dhcpcd.conf.d
cp config/hotspot/hostapd.conf /etc/hostapd/hostapd.conf
cp config/hotspot/dnsmasq.conf /etc/dnsmasq.conf
cp config/hotspot/routed-ap.conf /etc/dhcpcd.conf.d/receipt-ap.conf

# Ensure hostapd uses the custom config
if ! grep -q 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' /etc/default/hostapd 2>/dev/null; then
  echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> /etc/default/hostapd
fi

# Enable forwarding
if ! grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf; then
  echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
fi

# Persist iptables rules on boot
cp /home/pi/receipt-scanner/services/hotspot_nat.service /etc/systemd/system/hotspot_nat.service
systemctl enable hotspot_nat.service

# Enable core services
cp /home/pi/receipt-scanner/services/receipt_scanner.service /etc/systemd/system/receipt_scanner.service
cp /home/pi/receipt-scanner/services/battery_monitor.service /etc/systemd/system/battery_monitor.service
systemctl enable receipt_scanner.service
systemctl enable battery_monitor.service

systemctl enable hostapd
systemctl enable dnsmasq
EOFCHROOT

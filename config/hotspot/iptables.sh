#!/bin/bash
<< codex/build-raspberry-pi-receipt-scanner-project-q6udip
set -euo pipefail

# Ensure NAT and forwarding rules exist (idempotent). Designed to be run as root
# via systemd so sudo is intentionally avoided.
if ! iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null; then
  iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
fi

if ! iptables -C FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null; then
  iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
fi

if ! iptables -C FORWARD -i wlan0 -o eth0 -j ACCEPT 2>/dev/null; then
  iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
fi

iptables-save > /etc/iptables.ipv4.nat
=======
set -e
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
>> main

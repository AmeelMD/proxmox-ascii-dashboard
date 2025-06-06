#!/bin/bash
set -e

echo "🧹 Uninstalling Proxmox ASCII Dashboard..."

# Stop and disable services
systemctl stop proxmox-ascii-dashboard.service || true
systemctl stop proxmox-ascii-dashboard-watchdog.service || true
systemctl disable proxmox-ascii-dashboard.service || true
systemctl disable proxmox-ascii-dashboard-watchdog.service || true

# Remove systemd service files
rm -f /etc/systemd/system/proxmox-ascii-dashboard.service
rm -f /etc/systemd/system/proxmox-ascii-dashboard-watchdog.service

# Remove dashboard files
rm -rf /opt/ascii-dashboard

# Reload systemctl
systemctl daemon-reload

echo "✅ Uninstallation complete. All dashboard files and services removed."
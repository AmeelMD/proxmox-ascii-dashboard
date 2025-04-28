#!/bin/bash
set -e

echo "📦 Installing Proxmox ASCII Dashboard..."

# Create install directory
mkdir -p /opt/ascii-dashboard/assets

# Copy files
cp dashboard.py /opt/ascii-dashboard/
cp -r assets/* /opt/ascii-dashboard/assets/
cp requirements.txt /opt/ascii-dashboard/
cp LICENSE /opt/ascii-dashboard/
cp VERSION /opt/ascii-dashboard/
cp watchdog.sh /opt/ascii-dashboard/     # << ADD THIS

# Make watchdog.sh executable
chmod +x /opt/ascii-dashboard/watchdog.sh # << ADD THIS

# Install dependencies
apt update
apt install -y python3 python3-pip git

# Install required Python packages
pip3 install --upgrade pip
pip3 install -r /opt/ascii-dashboard/requirements.txt

# Copy service files
cp proxmox-ascii-dashboard.service /etc/systemd/system/
cp proxmox-ascii-dashboard-watchdog.service /etc/systemd/system/

# Enable and start services
systemctl daemon-reload
systemctl enable proxmox-ascii-dashboard.service
systemctl enable proxmox-ascii-dashboard-watchdog.service
systemctl start proxmox-ascii-dashboard.service
systemctl start proxmox-ascii-dashboard-watchdog.service

echo "✅ Installation complete. Dashboard will appear when system is idle!"
#!/bin/bash
set -e

echo "📦 Installing Proxmox ASCII Dashboard..."

# Make sure git, python3, pip3 are installed
apt update
apt install -y git python3 python3-pip

# Remove old non-git folder if exists
if [ -d "/opt/ascii-dashboard" ]; then
  if [ ! -d "/opt/ascii-dashboard/.git" ]; then
    echo "⚠️ Existing /opt/ascii-dashboard found but it's not a git repo. Removing..."
    rm -rf /opt/ascii-dashboard
  fi
fi

# Clone fresh repo
if [ ! -d "/opt/ascii-dashboard" ]; then
  git clone https://github.com/AmeelMD/proxmox-ascii-dashboard.git /opt/ascii-dashboard
else
  echo "⚡ Valid git repo already exists, pulling latest changes..."
  cd /opt/ascii-dashboard
  git pull
fi

# Make watchdog.sh executable
chmod +x /opt/ascii-dashboard/watchdog.sh

# Install required Python packages
pip3 install --upgrade pip --break-system-packages
pip3 install --break-system-packages -r /opt/ascii-dashboard/requirements.txt

# Copy systemd service files
cp /opt/ascii-dashboard/proxmox-ascii-dashboard.service /etc/systemd/system/
cp /opt/ascii-dashboard/proxmox-ascii-dashboard-watchdog.service /etc/systemd/system/

# Enable and start services
systemctl daemon-reload
systemctl enable proxmox-ascii-dashboard.service
systemctl enable proxmox-ascii-dashboard-watchdog.service
systemctl start proxmox-ascii-dashboard.service
systemctl start proxmox-ascii-dashboard-watchdog.service

echo "✅ Installation complete. Dashboard will appear when system is idle!"
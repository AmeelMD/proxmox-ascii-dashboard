#!/bin/bash

IDLE_TIMEOUT=30  # seconds

while true; do
    ACTIVE_USERS=$(who | grep tty1 || true)
    
    if [ -z "$ACTIVE_USERS" ]; then
        # No user logged into tty1
        if ! systemctl is-active --quiet proxmox-ascii-dashboard.service; then
            echo "👀 No active user detected. Restarting dashboard..."
            systemctl start proxmox-ascii-dashboard.service
        fi
    else
        # User is logged in, make sure dashboard is stopped
        if systemctl is-active --quiet proxmox-ascii-dashboard.service; then
            echo "👤 User active. Stopping dashboard..."
            systemctl stop proxmox-ascii-dashboard.service
        fi
    fi
    
    sleep $IDLE_TIMEOUT
done
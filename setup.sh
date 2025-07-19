#!/bin/bash

echo "🚀 Starting Raspberry Pi setup..."

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install necessary dependencies
sudo apt-get install -y python3 python3-pip git
sudo apt-get install python3-smbus

# Install Pygame
pip install --user pygame==2.5.2
sudo apt-get install libsdl2-mixer-2.0-0
sudo apt-get install libsdl2-ttf-2.0-0
pip install psutil
sudo apt install -y python3-dev python3-pip python3-setuptools \
    python3-wheel git build-essential \
    libfreetype6-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev \
    libsdl2-ttf-dev libportmidi-dev libjpeg-dev libtiff-dev \
    libwebp-dev libpng-dev libx11-dev libxcursor-dev \
    libxrandr-dev libxi-dev libgles2-mesa-dev libegl1-mesa-dev

# Create the Omnimon service
echo "[Unit]
Description=Start Omnimon at Boot
After=multi-user.target

[Service]
[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/Games/Omnimon
ExecStart=/bin/bash -c 'python3 vpet.py'
Restart=always
Environment="DISPLAY=:0"
Environment="PYTHONPATH=/home/admin/Games/Omnimon"
Environment="SDL_AUDIODRIVER=alsa"
Environment="XDG_RUNTIME_DIR=/run/user/1000"


[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/omnimon.service

# Set proper permissions for the service file
sudo chmod 644 /etc/systemd/system/omnimon.service
sudo chown root:root /etc/systemd/system/omnimon.service

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable omnimon.service
sudo systemctl start omnimon.service


echo "✅ Setup complete! Omnimon service created & enabled. Reboot recommended."

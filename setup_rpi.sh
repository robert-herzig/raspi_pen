#!/bin/bash
# Setup script for QR Scanner on Raspberry Pi Zero 2 W

echo "Setting up QR Scanner for Raspberry Pi Zero 2 W..."

# Update system
echo "Updating system packages..."
sudo apt update

# Install system dependencies for OpenCV and pyzbar
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-dev
sudo apt install -y libzbar0 libzbar-dev  # For pyzbar
sudo apt install -y libopencv-dev python3-opencv  # For OpenCV (lighter than pip version)

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install pyzbar

# Enable camera if not already enabled
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

echo "Setup complete!"
echo "You can now run the QR scanner with: python3 qr_scanner.py"
echo "Make sure to reboot if camera was just enabled: sudo reboot"

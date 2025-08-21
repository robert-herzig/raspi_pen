#!/bin/bash
# Setup script for QR Scanner on Raspberry Pi Zero 2 W

echo "Setting up QR Scanner for Raspberry Pi Zero 2 W..."

# Update system
echo "Updating system packages..."
sudo apt update

# Install system dependencies for OpenCV and pyzbar
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-dev python3-venv python3-full
sudo apt install -y libzbar0 libzbar-dev  # For pyzbar
sudo apt install -y libopencv-dev python3-opencv  # For OpenCV (lighter than pip version)

# Try to install pyzbar from system packages first
echo "Trying to install pyzbar from system packages..."
if sudo apt install -y python3-pyzbar; then
    echo "Successfully installed pyzbar from system packages"
    USE_VENV=false
else
    echo "pyzbar not available in system packages, will use virtual environment"
    USE_VENV=true
fi

# If system packages don't work, create virtual environment
if [ "$USE_VENV" = true ]; then
    echo "Creating virtual environment..."
    python3 -m venv qr_scanner_env
    
    echo "Activating virtual environment and installing pyzbar..."
    source qr_scanner_env/bin/activate
    pip install pyzbar
    deactivate
    
    echo "Created virtual environment at: $(pwd)/qr_scanner_env"
    echo "To use the scanner, first activate the environment:"
    echo "  source qr_scanner_env/bin/activate"
    echo "  python3 qr_scanner.py"
    echo "  deactivate  # when done"
fi

# Enable camera if not already enabled
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

echo "Setup complete!"
if [ "$USE_VENV" = true ]; then
    echo "Virtual environment created. To run the QR scanner:"
    echo "  source qr_scanner_env/bin/activate"
    echo "  python3 qr_scanner.py"
    echo "  deactivate"
else
    echo "You can now run the QR scanner with: python3 qr_scanner.py"
fi
echo "Make sure to reboot if camera was just enabled: sudo reboot"

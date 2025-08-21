#!/bin/bash
# Quick fix to install OpenCV in existing virtual environment

echo "Installing OpenCV in virtual environment..."

if [ -d "qr_scanner_env" ]; then
    source qr_scanner_env/bin/activate
    echo "Installing opencv-python..."
    pip install opencv-python
    deactivate
    echo "OpenCV installed successfully!"
    echo "You can now run: ./run_scanner.sh"
else
    echo "Virtual environment not found. Please run setup_rpi.sh first."
fi

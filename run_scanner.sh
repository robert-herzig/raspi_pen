#!/bin/bash
# Run script for QR Scanner

echo "QR Scanner for Raspberry Pi Zero 2 W"
echo "======================================"

# Check if virtual environment exists
if [ -d "qr_scanner_env" ]; then
    echo "Virtual environment found. Trying virtual environment version..."
    source qr_scanner_env/bin/activate
    
    # Check if cv2 is available in venv
    if python3 -c "import cv2" 2>/dev/null; then
        echo "Running with virtual environment (full opencv-python)..."
        python3 qr_scanner.py
    else
        echo "OpenCV not found in virtual environment."
        echo "Trying system version..."
        deactivate
        python3 qr_scanner_system.py
    fi
    
    # Make sure to deactivate if we're still in venv
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        deactivate
        echo "Virtual environment deactivated."
    fi
else
    echo "No virtual environment found. Using system packages..."
    python3 qr_scanner_system.py
fi

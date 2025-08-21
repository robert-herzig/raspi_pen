#!/bin/bash
# Run script for QR Scanner

# Check if virtual environment exists
if [ -d "qr_scanner_env" ]; then
    echo "Activating virtual environment..."
    source qr_scanner_env/bin/activate
    python3 qr_scanner.py
    deactivate
    echo "Virtual environment deactivated."
else
    echo "Running with system Python..."
    python3 qr_scanner.py
fi

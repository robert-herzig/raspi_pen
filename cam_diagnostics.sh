#!/bin/bash
echo "Raspberry Pi Camera Diagnostic Script"
echo "====================================="

echo "1. Checking GPU memory split..."
vcgencmd get_mem gpu

echo -e "\n2. Checking camera detection..."
vcgencmd get_camera

echo -e "\n3. Checking video devices..."
ls -la /dev/video*

echo -e "\n4. Checking camera modules..."
lsmod | grep -i camera
lsmod | grep -i bcm2835

echo -e "\n5. Checking V4L2 devices..."
if command -v v4l2-ctl &> /dev/null; then
    v4l2-ctl --list-devices
else
    echo "v4l2-ctl not installed"
fi

echo -e "\n6. Testing basic camera functionality..."
if command -v raspistill &> /dev/null; then
    echo "Testing raspistill (legacy camera stack)..."
    timeout 5s raspistill -t 1 -o /tmp/test.jpg 2>&1 || echo "raspistill test failed"
    if [ -f /tmp/test.jpg ]; then
        echo "raspistill test successful - image saved"
        rm /tmp/test.jpg
    fi
else
    echo "raspistill not available (using newer camera stack)"
fi

if command -v libcamera-still &> /dev/null; then
    echo "Testing libcamera-still (new camera stack)..."
    timeout 5s libcamera-still -t 1 -o /tmp/test.jpg 2>&1 || echo "libcamera-still test failed"
    if [ -f /tmp/test.jpg ]; then
        echo "libcamera-still test successful - image saved"
        rm /tmp/test.jpg
    fi
else
    echo "libcamera-still not available"
fi

echo -e "\n7. Memory information..."
free -h

echo -e "\n8. Recommended fixes:"
echo "If GPU memory is less than 128MB:"
echo "  sudo raspi-config -> Advanced Options -> Memory Split -> 128"
echo "If using legacy camera stack:"
echo "  Add 'start_x=1' to /boot/config.txt"
echo "If using new camera stack:"
echo "  Add 'dtoverlay=imx219' or appropriate camera overlay to /boot/config.txt"
echo "Then reboot: sudo reboot"
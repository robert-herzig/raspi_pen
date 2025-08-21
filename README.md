# QR Code Scanner for Raspberry Pi Zero 2 W

A lightweight Python script that uses the camera to detect and print QR code content on a Raspberry Pi Zero 2 W.

## Features

- Minimal dependencies for optimal performance on RPi Zero 2 W
- Real-time QR code detection and decoding
- Debounce logic to prevent duplicate readings
- Optimized camera settings for better performance
- Clean console output with QR code content

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Camera module (CSI camera or USB camera)

## Installation

### Quick Setup (Recommended)

1. Copy files to your Raspberry Pi
2. Make the setup script executable and run it:
   ```bash
   chmod +x setup_rpi.sh
   ./setup_rpi.sh
   ```

### Manual Setup

1. Update your system:
   ```bash
   sudo apt update
   ```

2. Install system dependencies:
   ```bash
   sudo apt install -y python3-pip python3-dev libzbar0 libzbar-dev libopencv-dev python3-opencv
   ```

3. Install Python dependencies:
   ```bash
   pip3 install pyzbar
   ```

4. Enable camera interface:
   ```bash
   sudo raspi-config nonint do_camera 0
   sudo reboot
   ```

## Usage

Run the QR scanner:
```bash
python3 qr_scanner.py
```

- Point the camera at a QR code
- The content will be printed to the console
- Press `Ctrl+C` to exit

## Configuration

You can modify the following parameters in `qr_scanner.py`:

- `camera_index`: Change camera source (default: 0)
- `debounce_time`: Time between duplicate QR code readings (default: 2 seconds)
- Camera resolution and FPS in the `start_camera()` method

## Troubleshooting

### Camera Issues
- Make sure the camera is properly connected
- Verify camera is enabled: `sudo raspi-config`
- Test camera: `raspistill -o test.jpg`

### Performance Issues
- Lower the camera resolution or FPS in the script
- Ensure good lighting conditions
- Keep QR codes at an appropriate distance from the camera

### Permission Issues
- Run with `sudo` if you encounter permission errors
- Make sure your user is in the `video` group: `sudo usermod -a -G video $USER`

## Dependencies

- `opencv-python`: Computer vision library for camera handling
- `pyzbar`: QR code decoding library

## Notes for Raspberry Pi Zero 2 W

This script is optimized for the limited resources of the RPi Zero 2 W:
- Uses system OpenCV instead of pip version when possible
- Lower camera resolution and FPS settings
- Minimal processing overhead
- Efficient memory usage

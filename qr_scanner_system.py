#!/usr/bin/env python3
"""
Lightweight QR Code Scanner for Raspberry Pi Zero 2 W
Uses system OpenCV to avoid heavy pip installations.
"""

import sys
import time
import os

# Check if we can import cv2 from system packages
try:
    import cv2
except ImportError:
    print("Error: OpenCV not found!")
    print("Please install system OpenCV: sudo apt install python3-opencv")
    sys.exit(1)

try:
    from pyzbar import pyzbar
except ImportError:
    print("Error: pyzbar not found!")
    print("Please install: pip install pyzbar (in virtual environment)")
    print("Or try: sudo apt install python3-pyzbar")
    sys.exit(1)


class QRScanner:
    def __init__(self, camera_index=0):
        """
        Initialize the QR scanner with camera.
        
        Args:
            camera_index (int): Camera index (usually 0 for RPi camera)
        """
        self.camera_index = camera_index
        self.cap = None
        self.last_qr_data = None
        self.last_qr_time = 0
        self.debounce_time = 2  # Prevent duplicate reads within 2 seconds
        
    def check_camera_devices(self):
        """Check available camera devices."""
        print("Checking available camera devices...")
        
        # Check for video devices
        video_devices = []
        for i in range(10):  # Check /dev/video0 to /dev/video9
            device_path = f"/dev/video{i}"
            if os.path.exists(device_path):
                video_devices.append(i)
                print(f"Found video device: {device_path}")
        
        if not video_devices:
            print("No video devices found!")
            print("Please check:")
            print("1. Camera is properly connected")
            print("2. Camera is enabled: sudo raspi-config -> Interface Options -> Camera")
            print("3. Try: sudo modprobe bcm2835-v4l2")
            return video_devices
        
        return video_devices
        
    def start_camera(self):
        """Initialize the camera capture."""
        try:
            # Check available devices first
            available_devices = self.check_camera_devices()
            if not available_devices:
                return False
            
            # Try each available device
            devices_to_try = available_devices if available_devices else [0, 1]
            
            for device_idx in devices_to_try:
                print(f"\nTrying device /dev/video{device_idx}...")
                
                # Try different approaches for this device
                approaches = [
                    # Approach 1: Direct V4L2 with specific settings
                    lambda idx: self._try_v4l2_direct(idx),
                    # Approach 2: Basic OpenCV with minimal settings
                    lambda idx: self._try_basic_opencv(idx),
                    # Approach 3: Legacy mode
                    lambda idx: self._try_legacy_mode(idx),
                ]
                
                for i, approach in enumerate(approaches):
                    print(f"  Approach {i+1}...")
                    if approach(device_idx):
                        print(f"  Success with approach {i+1}!")
                        return True
                    else:
                        print(f"  Approach {i+1} failed")
            
            print("All camera initialization attempts failed")
            return False
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def _try_v4l2_direct(self, device_idx):
        """Try V4L2 backend with specific settings."""
        try:
            # Release any existing capture
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Create capture with V4L2 backend
            self.cap = cv2.VideoCapture(device_idx, cv2.CAP_V4L2)
            
            if not self.cap.isOpened():
                return False
            
            # Set very conservative settings for RPi Zero 2 W
            settings_applied = 0
            
            # Try to set resolution (very low for memory constraints)
            if self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160):
                settings_applied += 1
            if self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120):
                settings_applied += 1
            if self.cap.set(cv2.CAP_PROP_FPS, 5):
                settings_applied += 1
            if self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1):
                settings_applied += 1
            
            # Try to set pixel format to YUYV (common and efficient)
            try:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
            except:
                pass
            
            print(f"    Applied {settings_applied}/4 camera settings")
            
            # Test if we can read frames
            for attempt in range(3):
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"    Frame test successful (size: {frame.shape})")
                    return True
                time.sleep(0.1)
            
            return False
            
        except Exception as e:
            print(f"    V4L2 approach error: {e}")
            return False
    
    def _try_basic_opencv(self, device_idx):
        """Try basic OpenCV approach."""
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Simple OpenCV capture
            self.cap = cv2.VideoCapture(device_idx)
            
            if not self.cap.isOpened():
                return False
            
            # Minimal settings
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame capture
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"    Basic OpenCV successful (size: {frame.shape})")
                return True
            
            return False
            
        except Exception as e:
            print(f"    Basic OpenCV error: {e}")
            return False
    
    def _try_legacy_mode(self, device_idx):
        """Try legacy compatibility mode."""
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Try with CAP_ANY and no initial settings
            self.cap = cv2.VideoCapture(device_idx, cv2.CAP_ANY)
            
            if not self.cap.isOpened():
                return False
            
            # Test without setting any properties first
            ret, frame = self.cap.read()
            if ret and frame is not None:
                print(f"    Legacy mode successful (size: {frame.shape})")
                # Only now try to optimize settings
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                return True
            
            return False
            
        except Exception as e:
            print(f"    Legacy mode error: {e}")
            return False
    
    def decode_qr_codes(self, frame):
        """
        Decode QR codes from the given frame.
        
        Args:
            frame: OpenCV frame/image
            
        Returns:
            list: List of decoded QR code data
        """
        try:
            # Convert to grayscale for better QR detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect and decode QR codes
            qr_codes = pyzbar.decode(gray)
            
            decoded_data = []
            for qr_code in qr_codes:
                # Extract the QR code data
                qr_data = qr_code.data.decode('utf-8')
                qr_type = qr_code.type
                
                decoded_data.append({
                    'data': qr_data,
                    'type': qr_type,
                    'rect': qr_code.rect
                })
                
            return decoded_data
        except Exception as e:
            print(f"Error decoding QR codes: {e}")
            return []
    
    def should_process_qr(self, qr_data):
        """
        Check if we should process this QR code (debounce logic).
        
        Args:
            qr_data (str): QR code data
            
        Returns:
            bool: True if should process, False otherwise
        """
        current_time = time.time()
        
        # If it's the same QR code and within debounce time, skip
        if (self.last_qr_data == qr_data and 
            current_time - self.last_qr_time < self.debounce_time):
            return False
            
        self.last_qr_data = qr_data
        self.last_qr_time = current_time
        return True
    
    def run(self):
        """Main scanning loop."""
        if not self.start_camera():
            print("\nTroubleshooting steps:")
            print("1. sudo raspi-config -> Interface Options -> Camera -> Enable")
            print("2. sudo modprobe bcm2835-v4l2")
            print("3. Reboot: sudo reboot")
            print("4. Check connections and try again")
            return
        
        print("\nQR Scanner started successfully!")
        print("Point the camera at a QR code to scan it.")
        print("Press Ctrl+C to exit.")
        print("-" * 50)
        
        frame_count = 0
        failed_frames = 0
        max_failed_frames = 10
        
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.cap.read()
                
                if not ret or frame is None or frame.size == 0:
                    failed_frames += 1
                    if failed_frames <= 3:  # Only show first few failures
                        print(f"Failed to capture frame {frame_count} (failed: {failed_frames})")
                    
                    if failed_frames >= max_failed_frames:
                        print(f"Too many failed frames ({failed_frames}), restarting camera...")
                        if self.start_camera():
                            failed_frames = 0
                            continue
                        else:
                            print("Camera restart failed, exiting...")
                            break
                    
                    time.sleep(0.5)
                    continue
                
                # Reset failed frame counter on success
                if failed_frames > 0:
                    print(f"Camera recovered after {failed_frames} failed frames")
                    failed_frames = 0
                
                frame_count += 1
                
                # Progress indicator (less frequent to reduce output spam)
                if frame_count % 50 == 0:
                    print(f"Scanning... (frame {frame_count})")
                
                # Decode QR codes in the frame
                qr_codes = self.decode_qr_codes(frame)
                
                # Process each detected QR code
                for qr_info in qr_codes:
                    qr_data = qr_info['data']
                    
                    if self.should_process_qr(qr_data):
                        print(f"\n🎯 QR Code detected!")
                        print(f"Type: {qr_info['type']}")
                        print(f"Content: {qr_data}")
                        print("-" * 50)
                
                # Longer delay for RPi Zero 2 W
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\nStopping QR scanner...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Camera resources released.")


def main():
    """Main function to run the QR scanner."""
    print("QR Scanner for Raspberry Pi Zero 2 W")
    print("Using system OpenCV for better performance")
    print("=" * 50)
    
    scanner = QRScanner()
    scanner.run()


if __name__ == "__main__":
    main()

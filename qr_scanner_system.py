#!/usr/bin/env python3
"""
Lightweight QR Code Scanner for Raspberry Pi Zero 2 W
Uses system OpenCV to avoid heavy pip installations.
"""

import sys
import time

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
        
    def start_camera(self):
        """Initialize the camera capture."""
        try:
            # Try different camera backends for Raspberry Pi
            backends_to_try = [
                cv2.CAP_V4L2,  # Video4Linux2 - most reliable on RPi
                cv2.CAP_GSTREAMER,  # GStreamer (if it works)
                cv2.CAP_ANY,  # Let OpenCV choose
            ]
            
            for backend in backends_to_try:
                print(f"Trying camera backend: {backend}")
                self.cap = cv2.VideoCapture(self.camera_index, backend)
                
                if self.cap.isOpened():
                    # Test if we can actually read a frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"Camera opened successfully with backend: {backend}")
                        break
                    else:
                        print(f"Backend {backend} opened but cannot read frames")
                        self.cap.release()
                        self.cap = None
                else:
                    print(f"Backend {backend} failed to open camera")
                    if self.cap:
                        self.cap.release()
                        self.cap = None
            
            if not self.cap or not self.cap.isOpened():
                raise RuntimeError("Could not open camera with any backend")
            
            # Set camera properties for better performance on RPi Zero 2 W
            # Use lower resolution and frame rate
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Lower resolution
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Lower resolution
            self.cap.set(cv2.CAP_PROP_FPS, 10)            # Lower FPS
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # Reduce buffer size
            
            # Try to set pixel format to reduce processing
            try:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            except:
                pass  # Ignore if not supported
            
            print("Camera configured for optimal RPi Zero 2 W performance")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure camera is enabled: sudo raspi-config")
            print("2. Check camera connection")
            print("3. Try: sudo modprobe bcm2835-v4l2")
            print("4. Check available cameras: ls /dev/video*")
            return False
    
    def decode_qr_codes(self, frame):
        """
        Decode QR codes from the given frame.
        
        Args:
            frame: OpenCV frame/image
            
        Returns:
            list: List of decoded QR code data
        """
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
            return
        
        print("QR Scanner started. Press Ctrl+C to exit.")
        print("Point the camera at a QR code to scan it.")
        print("-" * 50)
        
        frame_count = 0
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print(f"Failed to capture frame {frame_count}")
                    time.sleep(0.5)  # Wait a bit before retrying
                    continue
                
                frame_count += 1
                if frame_count % 30 == 0:  # Progress indicator every 30 frames
                    print(f"Scanning... (frame {frame_count})")
                
                # Decode QR codes in the frame
                qr_codes = self.decode_qr_codes(frame)
                
                # Process each detected QR code
                for qr_info in qr_codes:
                    qr_data = qr_info['data']
                    
                    if self.should_process_qr(qr_data):
                        print(f"QR Code detected!")
                        print(f"Type: {qr_info['type']}")
                        print(f"Content: {qr_data}")
                        print("-" * 50)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
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
    print()
    
    scanner = QRScanner()
    scanner.run()


if __name__ == "__main__":
    main()

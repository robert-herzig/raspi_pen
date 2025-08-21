#!/usr/bin/env python3
"""
QR Code Scanner for Raspberry Pi Zero 2 W
Lightweight script that uses the camera to detect and print QR code content.
"""

import cv2
import time
from pyzbar import pyzbar


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
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise RuntimeError("Could not open camera")
            
            # Set camera properties for better performance on RPi Zero 2 W
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 15)  # Lower FPS for better performance
            
            print("Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
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
        
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break
                
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
    scanner = QRScanner()
    scanner.run()


if __name__ == "__main__":
    main()

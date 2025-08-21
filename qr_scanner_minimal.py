#!/usr/bin/env python3
"""
Minimal QR Code Scanner for Raspberry Pi Zero 2 W
Uses direct V4L2 approach without OpenCV camera capture
"""

import sys
import time
import subprocess
import tempfile
import os

try:
    import cv2
except ImportError:
    print("Error: OpenCV not found!")
    print("Please install: sudo apt install python3-opencv")
    sys.exit(1)

try:
    from pyzbar import pyzbar
except ImportError:
    print("Error: pyzbar not found!")
    print("Please install: pip install pyzbar")
    sys.exit(1)


class MinimalQRScanner:
    def __init__(self):
        self.last_qr_data = None
        self.last_qr_time = 0
        self.debounce_time = 2
        self.temp_dir = tempfile.mkdtemp()
        
    def check_camera_tools(self):
        """Check what camera tools are available."""
        tools = {
            'raspistill': False,
            'libcamera-still': False,
            'fswebcam': False,
            'ffmpeg': False
        }
        
        for tool in tools.keys():
            try:
                result = subprocess.run(['which', tool], 
                                      capture_output=True, text=True)
                tools[tool] = result.returncode == 0
            except:
                pass
        
        print("Available camera tools:")
        for tool, available in tools.items():
            status = "✓" if available else "✗"
            print(f"  {status} {tool}")
        
        return tools
    
    def capture_image_raspistill(self, output_path):
        """Capture image using raspistill (legacy camera stack)."""
        try:
            cmd = [
                'raspistill',
                '-t', '1',  # 1ms timeout (immediate capture)
                '-w', '640',  # width
                '-h', '480',  # height
                '-q', '75',   # quality
                '-o', output_path,
                '--nopreview'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"raspistill error: {e}")
            return False
    
    def capture_image_libcamera(self, output_path):
        """Capture image using libcamera-still (new camera stack)."""
        try:
            cmd = [
                'libcamera-still',
                '-t', '1',  # 1ms timeout
                '--width', '640',
                '--height', '480',
                '--quality', '75',
                '-o', output_path,
                '--nopreview'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"libcamera-still error: {e}")
            return False
    
    def capture_image_fswebcam(self, output_path):
        """Capture image using fswebcam."""
        try:
            cmd = [
                'fswebcam',
                '-d', '/dev/video0',
                '-r', '640x480',
                '--no-banner',
                '--save', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"fswebcam error: {e}")
            return False
    
    def capture_image_ffmpeg(self, output_path):
        """Capture image using ffmpeg."""
        try:
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-i', '/dev/video0',
                '-vframes', '1',
                '-s', '640x480',
                '-y',  # overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"ffmpeg error: {e}")
            return False
    
    def capture_image(self):
        """Try to capture an image using available tools."""
        tools = self.check_camera_tools()
        output_path = os.path.join(self.temp_dir, 'capture.jpg')
        
        # Try tools in order of preference
        capture_methods = [
            ('libcamera-still', self.capture_image_libcamera),
            ('raspistill', self.capture_image_raspistill),
            ('fswebcam', self.capture_image_fswebcam),
            ('ffmpeg', self.capture_image_ffmpeg)
        ]
        
        for tool_name, capture_func in capture_methods:
            if tools.get(tool_name, False):
                print(f"Trying {tool_name}...")
                if capture_func(output_path):
                    print(f"✓ Successfully captured image with {tool_name}")
                    return output_path
                else:
                    print(f"✗ {tool_name} failed")
            else:
                print(f"✗ {tool_name} not available")
        
        return None
    
    def decode_qr_codes_from_file(self, image_path):
        """Decode QR codes from image file."""
        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Decode QR codes
            qr_codes = pyzbar.decode(gray)
            
            decoded_data = []
            for qr_code in qr_codes:
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
        """Check if we should process this QR code (debounce logic)."""
        current_time = time.time()
        
        if (self.last_qr_data == qr_data and 
            current_time - self.last_qr_time < self.debounce_time):
            return False
            
        self.last_qr_data = qr_data
        self.last_qr_time = current_time
        return True
    
    def run(self):
        """Main scanning loop."""
        print("Minimal QR Scanner for Raspberry Pi Zero 2 W")
        print("Using external camera tools instead of OpenCV capture")
        print("=" * 60)
        
        # Check available tools
        tools = self.check_camera_tools()
        if not any(tools.values()):
            print("\nNo camera tools available!")
            print("Install one of these:")
            print("  sudo apt install fswebcam")
            print("  sudo apt install ffmpeg")
            print("Or enable camera in raspi-config")
            return
        
        print(f"\nScanning for QR codes...")
        print("Press Ctrl+C to exit")
        print("-" * 40)
        
        scan_count = 0
        
        try:
            while True:
                scan_count += 1
                print(f"Scan {scan_count}...", end=" ")
                
                # Capture image
                image_path = self.capture_image()
                if not image_path:
                    print("capture failed")
                    time.sleep(2)
                    continue
                
                # Decode QR codes
                qr_codes = self.decode_qr_codes_from_file(image_path)
                
                if qr_codes:
                    print(f"found {len(qr_codes)} QR code(s)!")
                    for qr_info in qr_codes:
                        qr_data = qr_info['data']
                        if self.should_process_qr(qr_data):
                            print(f"\n🎯 QR Code Content:")
                            print(f"   Type: {qr_info['type']}")
                            print(f"   Data: {qr_data}")
                            print("-" * 40)
                else:
                    print("no QR codes found")
                
                # Clean up image file
                try:
                    os.remove(image_path)
                except:
                    pass
                
                # Wait before next scan
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nStopping QR scanner...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
        print("Cleanup complete.")


def main():
    scanner = MinimalQRScanner()
    scanner.run()


if __name__ == "__main__":
    main()
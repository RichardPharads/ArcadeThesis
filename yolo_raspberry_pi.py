#!/usr/bin/env python3
"""
YOLO Object Detection for Raspberry Pi 4 with Camera Module v2
Optimized for performance and resource efficiency
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

# Import picamera2 for Raspberry Pi Camera Module v2
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("Warning: picamera2 not available, falling back to OpenCV")

# Import OpenCV as fallback
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Error: OpenCV not available")

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Error: ultralytics not available")

# Import numpy for array operations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Error: numpy not available")

class RaspberryPiYOLO:
    def __init__(self):
        self.is_raspi = self._detect_raspberry_pi()
        self.model_path = self._get_model_path()
        self.camera_source = self._get_camera_source()
        
        # Detection settings
        self.confidence_threshold = 0.3
        self.bottle_class_id = 39  # COCO class index for 'bottle'
        self.launch_cooldown = 5  # seconds between launches
        self.last_launch_time = 0
        self.bottle_detected = False
        
        # Performance settings for Pi
        self.frame_skip = 2  # Process every nth frame
        self.frame_count = 0
        self.resolution = (640, 480)  # Lower resolution for better performance
        
        # Initialize components
        self.model = None
        self.camera = None
        self.running = False
        
        self._initialize_components()
    
    def _detect_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        if platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    return "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo
            except Exception:
                pass
        return False
    
    def _get_model_path(self):
        """Get the path to the YOLO model"""
        current_dir = Path(__file__).parent
        model_path = current_dir / "yoloModels" / "yolo11n.pt"
        
        # Fallback paths
        if not model_path.exists():
            model_path = current_dir / "yolo11n_ncnn_model" / "model_ncnn.py"
        
        if not model_path.exists():
            print(f"Warning: Model not found at {model_path}")
            return None
        
        return str(model_path)
    
    def _get_camera_source(self):
        """Get appropriate camera source for Raspberry Pi"""
        if self.is_raspi and PICAMERA2_AVAILABLE:
            return "picamera2"
        else:
            return 0  # Default camera index
    
    def _initialize_components(self):
        """Initialize YOLO model and camera"""
        # Initialize YOLO model
        if not YOLO_AVAILABLE:
            print("Error: ultralytics not available")
            return False
        
        if not self.model_path:
            print("Error: No model path available")
            return False
        
        try:
            print(f"Loading YOLO model from: {self.model_path}")
            self.model = YOLO(self.model_path)
            print("YOLO model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            return False
        
        # Initialize camera
        if self.camera_source == "picamera2":
            self._initialize_picamera2()
        else:
            self._initialize_opencv_camera()
        
        return True
    
    def _initialize_picamera2(self):
        """Initialize PiCamera2 for Camera Module v2"""
        try:
            self.camera = Picamera2()
            
            # Configure camera for optimal performance
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"},
                controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
            )
            self.camera.configure(config)
            
            # Start camera
            self.camera.start()
            print("PiCamera2 initialized successfully")
            
        except Exception as e:
            print(f"Error initializing PiCamera2: {e}")
            print("Falling back to OpenCV camera")
            self._initialize_opencv_camera()
    
    def _initialize_opencv_camera(self):
        """Initialize OpenCV camera as fallback"""
        try:
            self.camera = cv2.VideoCapture(self.camera_source)
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")
            
            print("OpenCV camera initialized successfully")
            
        except Exception as e:
            print(f"Error initializing OpenCV camera: {e}")
            self.camera = None
    
    def _capture_frame(self):
        """Capture a frame from the camera"""
        if self.camera_source == "picamera2" and self.camera:
            try:
                frame = self.camera.capture_array()
                return frame
            except Exception as e:
                print(f"Error capturing frame with PiCamera2: {e}")
                return None
        elif self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    return frame
                else:
                    return None
            except Exception as e:
                print(f"Error capturing frame with OpenCV: {e}")
                return None
        return None
    
    def _detect_bottles(self, frame):
        """Detect bottles in the frame using YOLO"""
        if not self.model or frame is None:
            return False
        
        try:
            # Run YOLO inference
            results = self.model.predict(
                source=frame,
                conf=self.confidence_threshold,
                classes=[self.bottle_class_id],
                verbose=False
            )
            
            # Check if bottles were detected
            for result in results:
                if len(result.boxes) > 0:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error during YOLO inference: {e}")
            return False
    
    def _launch_main_application(self):
        """Launch the main application"""
        current_time = time.time()
        if (current_time - self.last_launch_time) > self.launch_cooldown:
            self.last_launch_time = current_time
            print("Bottle detected! Launching main application...")
            
            try:
                current_dir = Path(__file__).parent
                main_script = current_dir / "main.py"
                
                if main_script.exists():
                    subprocess.Popen([sys.executable, str(main_script)])
                    print("Main application launched successfully")
                else:
                    print(f"Main script not found at: {main_script}")
                    
            except Exception as e:
                print(f"Error launching main application: {e}")
    
    def run(self):
        """Main detection loop"""
        if not self.camera:
            print("Error: No camera available")
            return
        
        print("Starting YOLO detection loop...")
        print("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                frame = self._capture_frame()
                if frame is None:
                    continue
                
                # Skip frames for better performance
                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    continue
                
                # Detect bottles
                bottle_found = self._detect_bottles(frame)
                
                # Handle bottle detection
                if bottle_found:
                    if not self.bottle_detected:
                        self.bottle_detected = True
                        self._launch_main_application()
                else:
                    self.bottle_detected = False
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping YOLO detection...")
        except Exception as e:
            print(f"Error in detection loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.camera:
            if self.camera_source == "picamera2":
                try:
                    self.camera.stop()
                    self.camera.close()
                except:
                    pass
            else:
                try:
                    self.camera.release()
                except:
                    pass
        
        # Close any OpenCV windows
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        print("Cleanup completed")

def main():
    """Main function"""
    print("Raspberry Pi YOLO Object Detection")
    print("=" * 40)
    
    # Check dependencies
    if not YOLO_AVAILABLE:
        print("Error: ultralytics not available. Please install with: pip install ultralytics")
        return
    
    if not NUMPY_AVAILABLE:
        print("Error: numpy not available. Please install with: pip install numpy")
        return
    
    if not PICAMERA2_AVAILABLE and not OPENCV_AVAILABLE:
        print("Error: No camera library available. Please install picamera2 or opencv-python")
        return
    
    # Create and run YOLO detector
    detector = RaspberryPiYOLO()
    detector.run()

if __name__ == "__main__":
    main() 
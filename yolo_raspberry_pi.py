#!/usr/bin/env python3
"""
Simple YOLO11n Detection for Raspberry Pi
Optimized for performance and ease of use
"""

import cv2
import numpy as np
import time
import os
import sys
from pathlib import Path

# Try to import picamera2 for Pi Camera Module v2
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
    print("✓ PiCamera2 available - using optimized camera interface")
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("⚠ PiCamera2 not available - using OpenCV camera")

# Try to import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    print("✓ YOLO available")
except ImportError:
    YOLO_AVAILABLE = False
    print("❌ YOLO not available - please install: pip install ultralytics")

class SimpleYOLODetector:
    def __init__(self):
        self.camera = None
        self.model = None
        self.running = False
        
        # Detection settings
        self.confidence_threshold = 0.5
        self.class_names = {
            39: "bottle",  # COCO class for bottle
            0: "person",   # COCO class for person
            1: "bicycle",  # COCO class for bicycle
            2: "car",      # COCO class for car
            3: "motorcycle" # COCO class for motorcycle
        }
        
        # Performance settings for Pi
        self.frame_skip = 3  # Process every 3rd frame
        self.frame_count = 0
        self.resolution = (640, 480)
        
        self.initialize()
    
    def initialize(self):
        """Initialize camera and YOLO model"""
        print("Initializing YOLO detector...")
        
        # Initialize YOLO model
        if not YOLO_AVAILABLE:
            print("❌ Cannot initialize - YOLO not available")
            return False
        
        try:
            # Try to find the model file
            model_paths = [
                "yolo11n.pt",
                "yoloModels/yolo11n.pt",
                "../yoloModels/yolo11n.pt"
            ]
            
            model_found = False
            for path in model_paths:
                if os.path.exists(path):
                    print(f"✓ Loading YOLO model from: {path}")
                    self.model = YOLO(path)
                    model_found = True
                    break
            
            if not model_found:
                print("⚠ Model not found locally, downloading YOLOv8n...")
                self.model = YOLO('yolov8n.pt')  # Download lightweight model
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            return False
        
        # Initialize camera
        if not self.initialize_camera():
            print("❌ Failed to initialize camera")
            return False
        
        print("✓ YOLO detector initialized successfully!")
        return True
    
    def initialize_camera(self):
        """Initialize camera (PiCamera2 or OpenCV)"""
        if PICAMERA2_AVAILABLE:
            return self.initialize_picamera2()
        else:
            return self.initialize_opencv_camera()
    
    def initialize_picamera2(self):
        """Initialize PiCamera2 for Camera Module v2"""
        try:
            self.camera = Picamera2()
            
            # Configure for optimal performance
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"},
                controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
            )
            self.camera.configure(config)
            self.camera.start()
            
            print("✓ PiCamera2 initialized")
            return True
            
        except Exception as e:
            print(f"❌ PiCamera2 error: {e}")
            print("Falling back to OpenCV...")
            return self.initialize_opencv_camera()
    
    def initialize_opencv_camera(self):
        """Initialize OpenCV camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")
            
            print("✓ OpenCV camera initialized")
            return True
            
        except Exception as e:
            print(f"❌ OpenCV camera error: {e}")
            return False
    
    def capture_frame(self):
        """Capture a frame from camera"""
        if PICAMERA2_AVAILABLE and self.camera:
            try:
                frame = self.camera.capture_array()
                return frame
            except Exception as e:
                print(f"PiCamera2 capture error: {e}")
                return None
        elif self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    return frame
                else:
                    return None
            except Exception as e:
                print(f"OpenCV capture error: {e}")
                return None
        return None
    
    def detect_objects(self, frame):
        """Run YOLO detection on frame"""
        if not self.model or frame is None:
            return []
        
        try:
            # Run YOLO inference
            results = self.model.predict(
                source=frame,
                conf=self.confidence_threshold,
                verbose=False
            )
            
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Get detection info
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Get class name
                        class_name = self.class_names.get(class_id, f"class_{class_id}")
                        
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name
                        })
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes on frame"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class_name']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Background for text
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # Text
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def run_detection(self):
        """Main detection loop"""
        if not self.camera:
            print("❌ No camera available")
            return
        
        print("🎯 Starting YOLO detection...")
        print("Press 'q' to quit, 's' to save frame")
        
        self.running = True
        fps_counter = 0
        fps_start_time = time.time()
        
        try:
            while self.running:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    continue
                
                # Skip frames for performance
                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    continue
                
                # Run detection
                detections = self.detect_objects(frame)
                
                # Draw detections
                frame = self.draw_detections(frame, detections)
                
                # Calculate FPS
                fps_counter += 1
                if fps_counter % 30 == 0:
                    current_time = time.time()
                    fps = 30 / (current_time - fps_start_time)
                    fps_start_time = current_time
                    print(f"FPS: {fps:.1f} | Detections: {len(detections)}")
                
                # Show frame
                cv2.imshow("YOLO Detection", frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"detection_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"✓ Frame saved as: {filename}")
                
        except KeyboardInterrupt:
            print("\n⏹ Stopping detection...")
        except Exception as e:
            print(f"❌ Error in detection loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.camera:
            if PICAMERA2_AVAILABLE:
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
        
        cv2.destroyAllWindows()
        print("✓ Cleanup completed")

def main():
    """Main function"""
    print("=" * 50)
    print("🎯 Simple YOLO11n Detection for Raspberry Pi")
    print("=" * 50)
    
    # Check dependencies
    if not YOLO_AVAILABLE:
        print("❌ Please install ultralytics: pip install ultralytics")
        return
    
    # Create and run detector
    detector = SimpleYOLODetector()
    detector.run_detection()

if __name__ == "__main__":
    main() 
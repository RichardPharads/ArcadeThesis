from ultralytics import YOLO
import subprocess
import sys
import os
import time

# For Pi camera support
try:
    from picamera2 import Picamera2
    import cv2
    USE_PI_CAMERA = True
except ImportError:
    USE_PI_CAMERA = False


def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    sys.exit(0)

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

if USE_PI_CAMERA:
    # Use PiCamera2 for video capture
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)  # Camera warm-up
    
    try:
        while True:
            frame = picam2.capture_array()
            results = model.predict(
                source=frame,
                show=True,
                conf=0.3,
                classes=[39],
                stream=False
            )
            if results and len(results[0].boxes) > 0:
                current_time = time.time()
                if not bottle_detected and (current_time - last_launch_time) > LAUNCH_COOLDOWN:
                    bottle_detected = True
                    last_launch_time = current_time
                    print("Bottle detected! Launching main application and closing YOLO...")
                    launch_main()
            else:
                bottle_detected = False
    except KeyboardInterrupt:
        print("\nStopping video capture...")
        sys.exit(0)
else:
    # Fallback to default webcam (USB)
    results = model.predict(
        source=0,             # 0 = default webcam
        show=True,            # Show the live feed with predictions
        conf=0.3,             # Confidence threshold
        classes=[39],         # COCO class index for 'bottle'
        stream=True           # Enable real-time streaming
    )
    try:
        for result in results:
            if len(result.boxes) > 0:
                current_time = time.time()
                if not bottle_detected and (current_time - last_launch_time) > LAUNCH_COOLDOWN:
                    bottle_detected = True
                    last_launch_time = current_time
                    print("Bottle detected! Launching main application and closing YOLO...")
                    launch_main()
            else:
                bottle_detected = False
    except KeyboardInterrupt:
        print("\nStopping video capture...")
        sys.exit(0) 
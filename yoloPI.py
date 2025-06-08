from ultralytics import YOLO
import subprocess
import sys
import os
import time
from picamera2 import Picamera2
from picamera2.previews import Preview

def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    # Close the current script after launching main.py
    sys.exit(0)

# Initialize Pi Camera
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(preview_config)
picam2.start()

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

# Start video capture using Pi Camera
results = model.predict(
    source=picam2.camera_id,  # Use Pi Camera as source
    show=True,                # Show the live feed with predictions
    conf=0.3,                 # Confidence threshold
    classes=[39],             # COCO class index for 'bottle'
    stream=True               # Enable real-time streaming
)

try:
    # Keep the video stream running
    for result in results:
        # Check if any bottles were detected
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
    picam2.stop()
    sys.exit(0) 
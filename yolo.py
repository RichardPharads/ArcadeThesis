from ultralytics import YOLO
import subprocess
import sys
import os
import time

def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    # Close the current script after launching main.py
    sys.exit(0)

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

# Start video capture
results = model.predict(
    source=0,             # 0 = default webcam
    show=True,            # Show the live feed with predictions
    conf=0.3,             # Confidence threshold
    classes=[39 ,0],         # COCO class index for 'bottle'
    stream=True           # Enable real-time streaming
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
    sys.exit(0)

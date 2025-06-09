from ultralytics import YOLO
import subprocess
import sys
import os
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    # Close the current script after launching main.py
    sys.exit(0)

# Initialize Raspberry Pi Camera
print("Initializing Raspberry Pi Camera...")
picam2 = Picamera2()

# Configure camera
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(preview_config)

# Start camera
picam2.start()
print("Camera started successfully")

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

try:
    while True:
        # Capture frame from PiCamera
        frame = picam2.capture_array()
        
        # Convert frame to RGB (YOLO expects RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run YOLO prediction on the frame
        results = model.predict(
            source=frame_rgb,
            show=True,
            conf=0.3,
            classes=[39, 0],  # COCO class index for 'bottle'
            stream=False
        )

        # Check if any bottles were detected
        if len(results[0].boxes) > 0:
            current_time = time.time()
            if not bottle_detected and (current_time - last_launch_time) > LAUNCH_COOLDOWN:
                bottle_detected = True
                last_launch_time = current_time
                print("Bottle detected! Launching main application and closing YOLO...")
                launch_main()
        else:
            bottle_detected = False

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping video capture...")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    picam2.stop()
    cv2.destroyAllWindows()
    sys.exit(0) 
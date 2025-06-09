from ultralytics import YOLO
import subprocess
import sys
import os
import time
import cv2

def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    # Close the current script after launching main.py
    sys.exit(0)

# Initialize camera using OpenCV
cap = cv2.VideoCapture(0)  # Use 0 for default camera, or try 1,2,etc. for other cameras
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Run YOLO prediction on the frame
        results = model.predict(
            source=frame,
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
finally:
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0) 
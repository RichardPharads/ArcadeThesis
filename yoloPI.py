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
print("Attempting to initialize camera...")
cap = cv2.VideoCapture(1)  # Try changing 0 to 1 or 2

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera. Please check if:")
    print("1. Your camera is properly connected")
    print("2. No other application is using the camera")
    print("3. You have the necessary permissions to access the camera")
    sys.exit(1)

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Verify camera properties were set correctly
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Camera initialized with resolution: {width}x{height}")

model = YOLO("../yoloModels/yolo11n.pt")
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Possible causes:")
            print("1. Camera disconnected")
            print("2. Camera is being used by another application")
            print("3. Camera driver issues")
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
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0) 
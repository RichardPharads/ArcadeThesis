from ultralytics import YOLO
import subprocess
import sys
import os
import time
import platform

def launch_main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen([sys.executable, os.path.join(current_dir, "main.py")])
    # Close the current script after launching main.py
    sys.exit(0)

# Detect if running on Raspberry Pi
is_raspi = False
if platform.system() == "Linux":
    # Check for Raspberry Pi in /proc/cpuinfo
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            if "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo:
                is_raspi = True
    except Exception:
        pass

# Set model path and camera source based on platform
def get_model_and_source():
    if is_raspi:
        # Adjust these paths if your model is elsewhere on the Pi
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../yoloModels/yolo11n.pt")
        # For Pi Camera, you might need to use a special source string or index
        # Try 0 for USB webcam, or '0' or 'libcamera' for Pi Camera
        # If using Pi Camera with OpenCV, you may need to install extra drivers
        camera_source = 0  # Change to '0' or 'libcamera' if needed
    else:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../yoloModels/yolo11n.pt")
        camera_source = 0
    return model_path, camera_source

model_path, camera_source = get_model_and_source()
model = YOLO(model_path)
bottle_detected = False
last_launch_time = 0
LAUNCH_COOLDOWN = 5  # Minimum seconds between launches

# Start video capture
results = model.predict(
    source=camera_source,   # Use platform-appropriate camera source
    show=True,              # Show the live feed with predictions
    conf=0.3,               # Confidence threshold
    classes=[39],           # COCO class index for 'bottle'
    stream=True             # Enable real-time streaming
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

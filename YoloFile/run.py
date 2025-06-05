from ultralytics import YOLO
import cv2
import sys
import os
from picamera2 import Picamera2
from picamera2.previews import Preview
import time

def show_alert():
    """Opens main.py when water bottle is detected."""
    try:
        # Get the parent directory path and run main.py from there
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_path = os.path.join(parent_dir, 'main.py')
        os.system(f'python "{main_path}"')  # Run main.py with full path
    except Exception as e:
        print(f"Error running main.py: {e}")
    sys.exit(0)

def load_yolo_model(model_path="yolo11n.pt"):
    """Loads the YOLO model with error handling."""
    print("Loading YOLO model...")
    try:
        # Check if model file exists
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found. Downloading default model...")
            model = YOLO("./yolo11n.pt")  # Download default model
        else:
            model = YOLO(model_path)
        print("YOLO model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Attempting to download default model...")
        try:
            model = YOLO("yolov8n.pt")
            print("Default model downloaded and loaded successfully.")
            return model
        except Exception as e:
            print(f"Failed to load default model: {e}")
            sys.exit(1)

def process_video_stream(model, conf_threshold=0.25):
    """Processes video stream from Raspberry Pi Camera for object detection."""
    print("Starting object detection...")
    try:
        # Initialize the camera
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(preview_config)
        picam2.start()
        
        # Give the camera time to warm up
        time.sleep(2)

        while True:
            # Capture frame from camera
            frame = picam2.capture_array()
            
            # Convert frame to RGB (YOLO expects RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run YOLO detection
            results = model(frame_rgb, conf=conf_threshold)
            
            # Process results
            for r in results:
                # Display the frame
                cv2.imshow('Raspberry Pi Camera', frame)
                
                # Check if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Quitting: 'q' pressed")
                    return
                
                # Check for water bottle detection
                if r.boxes:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = model.names[cls]
                        
                        if class_name == 'bottle' and conf > conf_threshold:
                            print("Water bottle detected!")
                            cv2.destroyAllWindows()
                            show_alert()
                            return

    except Exception as e:
        print(f"Error during video processing: {e}")
    finally:
        cv2.destroyAllWindows()
        picam2.stop()
        print("Processing complete.")

if __name__ == "__main__":
    # Load the model
    yolo_model = load_yolo_model()

    # Start processing camera feed
    process_video_stream(yolo_model)

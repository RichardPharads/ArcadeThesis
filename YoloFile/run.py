from ultralytics import YOLO
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import sys
import os

def show_alert():
    """Opens main.py when water bottle is detected."""
    cv2.destroyAllWindows()  # Close the OpenCV window
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

def process_video_stream(model, source=0, conf_threshold=0.25):
    """Processes a video stream for object detection."""
    print("Starting object detection...")
    try:
        results = model(source, 
                        show=True,  # Show the video feed
                        save=True,  # Save the video
                        conf=conf_threshold,  # Confidence threshold
                        stream=True)  # Enable streaming mode

        # Process the results frame by frame
        for r in results:
            # Check if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quitting: 'q' pressed")
                break
            
            # Check for water bottle detection
            if r.boxes:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls]
                    
                    if class_name == 'bottle' and conf > conf_threshold:
                        print("Water bottle detected!")
                        cv2.destroyAllWindows() # Close the OpenCV window
                        show_alert() # Show PyQt6 window and exit

    except Exception as e:
        print(f"Error during video processing: {e}")
    finally:
        cv2.destroyAllWindows()
        print("Processing complete.")

if __name__ == "__main__":
    # Load the model
    yolo_model = load_yolo_model()

    # Start processing webcam feed (source=0)
    process_video_stream(yolo_model, source=0)

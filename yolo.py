from ultralytics import YOLO

model = YOLO("yolo11n.pt")

# Start video capture
results = model.predict(
    source=0,             # 0 = default webcam
    show=True,            # Show the live feed with predictions
    conf=0.3,             # Confidence threshold
    classes=[39],         # COCO class index for 'bottle'
    stream=True           # Enable real-time streaming
)

# Keep the video stream running
for result in results:
    # The video will be shown automatically because show=True
    pass

from ultralytics import YOLO

# Load your trained model
model = YOLO(r"C:\Users\Asus\OneDrive\Desktop\python-workspace\runs\detect\train2\weights\best.pt")

# Run inference on the input video with a confidence threshold of 0.7
results = model.predict(
    source=r"C:\Users\Asus\OneDrive\Desktop\python-workspace\work6.mp4",
    conf=0.6,     # <-- Set confidence threshold here
    save=True     # Save output video with bounding boxes
)

# Print summary
print("Inference complete. Output saved to:", results[0].save_dir)

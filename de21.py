# THE FINAL WITH AREA AND DATABASE STORE

import cv2
import os
import sqlite3
from datetime import datetime
from ultralytics import YOLO

# === Connect to Existing Database ===
db_path = r"C:\Users\Asus\OneDrive\Desktop\python-workspace\ppe_web\violationss2.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# === Load YOLO Model ===
model = YOLO(r"C:\Users\Asus\OneDrive\Desktop\python-workspace\runs\detect\train5\weights\best.pt")

# === Violation Setup ===
violation_colors = {
    "No Helmet": (0, 0, 255),
    "No Golves": (0, 165, 255),
    "No Safety Boots": (0, 255, 255),
    "No Safety Glass": (255, 0, 0),
    "No IFR": (255, 255, 0),
}
violation_classes = list(violation_colors.keys())

# === Directory Setup ===
base_output_dir = "violations_video"
run_folder_name = datetime.now().strftime("run_%Y%m%d_%H%M%S")
output_dir = os.path.join(base_output_dir, run_folder_name)
os.makedirs(output_dir, exist_ok=True)
print(f"Saving violation screenshots to folder:\n{os.path.abspath(output_dir)}\n")

# === Load Video ===
video_path = r"C:\Users\Asus\OneDrive\Desktop\python-workspace\work4.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
interval_seconds = 70
frame_interval = int(fps * interval_seconds)

frame_count = 0
saved_violations = 0

# === Area Detection Logic ===
def get_area(x, frame_width):
    if x < frame_width / 3:
        return "Zone A [Construction-Block]"
    elif x < (2 * frame_width / 3):
        return "Zone B [Chemical-Block]"
    else:
        return "Zone C [Battery-Area]"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_interval != 0:
        continue

    frame_height, frame_width = frame.shape[:2]
    results = model(frame, conf=0.3)[0]
    annotated_frame = frame.copy()
    detected_violations = set()
    people_count = 0
    violation_area = "Unknown"

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "People":
            people_count += 1
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        elif label in violation_classes:
            detected_violations.add(label)
            color = violation_colors[label]
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Determine area from violation bounding box center
            x_center = (x1 + x2) // 2
            violation_area = get_area(x_center, frame_width)

    if detected_violations:
        if people_count == 0:
            people_count = 1

        timestamp_now = datetime.now()
        timestamp_str = timestamp_now.strftime("%Y-%m-%d %H:%M:%S")
        timestamp_for_file = timestamp_now.strftime("%Y%m%d_%H%M%S")

        violation_summary = ", ".join(sorted(detected_violations))
        violation_count = len(detected_violations)

        # Save violation image
        filename = f"violation_{timestamp_for_file}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, annotated_frame)

        # Convert image to bytes for DB storage
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        image_bytes = buffer.tobytes()

        # Insert into database including area
        cursor.execute("""
            INSERT INTO violations (frame_number, timestamp, violations, people_count, violation_count, area, violation_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (frame_count, timestamp_str, violation_summary, people_count, violation_count, violation_area, image_bytes))
        conn.commit()

        saved_violations += 1
        print(f"[{frame_count}] Violation saved: {violation_summary} in {violation_area} with {people_count} people")

cap.release()
conn.close()

print(f"\n✅ Done! Total frames processed: {frame_count}")
print(f"📸 Total violation screenshots saved: {saved_violations}")
print(f"\nAll screenshots are saved inside:\n{os.path.abspath(output_dir)}")
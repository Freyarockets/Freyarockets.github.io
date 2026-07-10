import csv
from datetime import datetime
import os
from pathlib import Path
import cv2
from ultralytics import YOLO

def process_images_with_reporting():
    # ==================== CONFIGURATION ====================
    TARGET_INPUT_FOLDER = "./trajectory"
    TARGET_OUTPUT_FOLDER = "./trajectory_results"
    CSV_REPORT_PATH = "./trajectory_results/detection_report.csv"

    # Define your whitelist. Empty set means "process and detect everything"
    # Example: {"person", "car", "motorcycle", "backpack"}
    CLASS_FILTER_WHITELIST = {"person", "car"} 
    # =======================================================

    # 1. Load the pre-trained YOLOv8 nano model
    model = YOLO("yolov8n.pt")

    # 2. Setup directories safely
    input_dir = Path(TARGET_INPUT_FOLDER)
    output_dir = Path(TARGET_OUTPUT_FOLDER)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Filter for compatible file extensions
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    image_paths = [p for p in input_dir.iterdir() if p.suffix.lower() in valid_extensions]
    
    if not image_paths:
        print(f"No valid images found in: '{TARGET_INPUT_FOLDER}'")
        return

    print(f"Found {len(image_paths)} images. Commencing isolated filter pipeline...")

    # 4. Initialize CSV layout fields
    csv_headers = ["Timestamp", "File Name", "Object Name", "Confidence Score", "Box Coordinates (xyxy)"]
    
    with open(CSV_REPORT_PATH, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csv_headers)

        for img_path in image_paths:
            # Run model on file pathway
            results = model(str(img_path))[0]
            
            # Temporary holder for target boxes to determine if we keep the image
            matched_detections = []
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 5. Extract bounding boxes, class ids, and scores
            # Reference: https://ultralytics.com
            for box in results.boxes:
                class_id = int(box.cls[0])
                object_name = model.names[class_id] # Convert ID to label name
                confidence = float(box.conf[0])
                coordinates = [round(float(c), 2) for c in box.xyxy[0].tolist()]

                # Filter condition: Check if it's in our whitelist
                if not CLASS_FILTER_WHITELIST or object_name in CLASS_FILTER_WHITELIST:
                    matched_detections.append({
                        "name": object_name,
                        "conf": confidence,
                        "coords": coordinates
                    })
                    
                    # Log object item instantly down into spreadsheet stream
                    writer.writerow([current_timestamp, img_path.name, object_name, f"{confidence:.4f}", coordinates])

            # 6. Saving Phase (Conditional Constraint Check)
            if matched_detections:
                print(f"✓ Match Found in {img_path.name}: Saved {len(matched_detections)} items.")
                
                # Plot bounding boxes ONLY for whitelisted items by using raw opencv 
                # or leveraging standard results plotting matrix 
                annotated_image = results.plot()
                save_path = output_dir / f"filtered_{img_path.name}"
                cv2.imwrite(str(save_path), annotated_image)
            else:
                print(f"⚠️ Skipped {img_path.name}: Contains no whitelisted objects.")

    print(f"\nProcessing Complete!")
    print(f"📁 Labeled Images Directory: {output_dir.resolve()}")
    print(f"📊 Spreadsheet Log File: {Path(CSV_REPORT_PATH).resolve()}")

if __name__ == "__main__":
    process_images_with_reporting()

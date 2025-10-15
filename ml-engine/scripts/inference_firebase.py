# scripts/inference_firebase.py
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, firestore
import os

# ---- Firebase setup ----
# Make sure firebase/serviceAccountKey.json exists
cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase", "serviceAccountKey.json")
if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Firebase service account not found at: {cred_path}")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ---- Load YOLO model (will download weights automatically if needed) ----
# Use 'yolov8n.pt' (nano) for a quick test
model = YOLO("yolov8n.pt")

def detect_issue(image_path):
    """
    Run model on image_path, print detected classes and optionally
    push a simple report document to Firestore for testing.
    """
    print(f"Running inference on: {image_path}")
    results = model(image_path)  # runs inference
    # results[0].boxes.cls contains predicted class indices
    detected = []
    if len(results) > 0 and hasattr(results[0], "boxes") and results[0].boxes is not None:
        for cls_idx in results[0].boxes.cls:
            # cls_idx is a Tensor; convert to int
            try:
                c = int(cls_idx)
            except Exception:
                c = int(cls_idx.item())
            detected.append(results[0].names[c])
    print("Detected classes:", detected)

    # Example: create a simple report in Firestore (for testing)
    # WARNING: this writes to your Firestore project
    report = {
        "image": os.path.basename(image_path),
        "detected": detected,
        "status": "test",
    }
    doc_ref = db.collection("test_reports").document()
    doc_ref.set(report)
    print(f"Pushed test report to Firestore (id={doc_ref.id})")

if __name__ == "__main__":
    # Path to your test image (relative to project root)
    test_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_image.jpg")
    if not os.path.exists(test_image):
        raise FileNotFoundError(f"Test image not found at: {test_image}. Please add a test_image.jpg in project root.")
    detect_issue(test_image)

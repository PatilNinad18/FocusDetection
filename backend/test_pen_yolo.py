from ultralytics import YOLO
import cv2

# Load the trained YOLO model
model = YOLO("E:/Focus_Detection/backend/models/pen_detectorv2.pt")

# Initialize webcam
cap = cv2.VideoCapture(0)

# ✅ Optional: Increase resolution for better pen detection at distance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("🖊️ Testing Pen Detection... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera not accessible or frame not captured.")
        break

    # Run YOLO inference
    results = model(frame, conf=0.35, verbose=False)  # lower conf=0.35 for small/far pens

    pen_detected = False

    # Loop through detections
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls)
            cls_name = model.names[cls_id]
            conf = float(box.conf)

            # Detect "pen" class
            if "pen" in cls_name.lower():
                pen_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                color = (255, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, max(30, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Add status text on screen
    if pen_detected:
        text = "✍️ Pen Detected"
        color = (0, 255, 0)
    else:
        text = "⚠️ No Pen Detected"
        color = (0, 0, 255)

    cv2.putText(frame, text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    # Display the output frame
    cv2.imshow("Pen Detection (Trained Model)", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2

class PhoneDetector:
    def __init__(self, model_path="models/yolov8n.pt"):
        """
        Detect mobile phones using a pretrained YOLOv8 model.
        """
        self.model = YOLO(model_path)

    def analyze_frame(self, frame):
        """
        Run phone detection on a frame.
        Returns:
            mobile_detected (bool): True if a phone is seen.
            frame (np.ndarray): Frame with bounding boxes drawn.
        """
        results = self.model(frame, conf=0.35, verbose=False)
        mobile_detected = False

        for r in results:
            for box in r.boxes:
                cls_name = self.model.names[int(box.cls)]
                conf = float(box.conf)

                if "cell phone" in cls_name.lower() or "mobile" in cls_name.lower():
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    width, height = x2 - x1, y2 - y1

                    # Ignore small detections (likely pen)
                    if width < 80 and height < 80:
                        continue

                    mobile_detected = True
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


        return mobile_detected, frame

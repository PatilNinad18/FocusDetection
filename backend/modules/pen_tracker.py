from ultralytics import YOLO
import cv2
import time

class PenTracker:
    def __init__(self, model_path="models/pen_detectorv2.pt", idle_threshold=300):
        """
        Detect pen presence and track writing activity.
        idle_threshold = seconds before considered 'not writing'
        """
        self.model = YOLO(model_path)
        self.last_seen_time = time.time()
        self.pen_detected = False
        self.idle_threshold = idle_threshold

    def analyze_frame(self, frame):
        results = self.model(frame, conf=0.35, verbose=False)
        pen_detected_now = False

        for r in results:
            for box in r.boxes:
                cls_name = self.model.names[int(box.cls)]
                if "pen" in cls_name.lower():
                    pen_detected_now = True
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    cv2.putText(frame, "Pen", (x1, max(30, y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Update detection logic
        if pen_detected_now:
            self.last_seen_time = time.time()
            self.pen_detected = True
        else:
            self.pen_detected = False

        idle_time = time.time() - self.last_seen_time
        return self.pen_detected, idle_time, frame

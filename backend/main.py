import cv2
import time
import json
import os

from modules.face_eye_tracker import FaceEyeTracker
from modules.phone_detector import PhoneDetector
from modules.pen_tracker import PenTracker
from modules.alerts import alert_user
from utils.focus_score import calculate_focus_score


def main():
    # Initialize all detectors
    face_tracker = FaceEyeTracker()
    phone_detector = PhoneDetector()
    pen_tracker = PenTracker()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not access the webcam.")
        return

    print("🎥 AI Focus Tracker Started — Press 'q' to quit.\n")

    # Create JSON file path for focus data
    # json_path = os.path.join(os.path.dirname(__file__), "focus_data.json")
    # Always save JSON to backend/focus_data.json (absolute path)
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_data.json")
    print(f"🟢 Writing focus data to: {json_path}")


    last_save_time = 0
    distractions = 0
    smooth_score = 100  # initial focus score

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed. Exiting...")
            break

        # Run detectors (each may draw on the frame and return updated frame)
        face_detected, eyes_closed, looking_away, base_score = face_tracker.analyze_frame(frame)
        phone_detected, frame = phone_detector.analyze_frame(frame)
        pen_detected, idle_time, frame = pen_tracker.analyze_frame(frame)

        # --- Compute focus score ---
        # calculate_focus_score expects: face_detected, eyes_closed, mobile_detected, pen_detected
        focus_score = calculate_focus_score(face_detected, eyes_closed, phone_detected, pen_detected)

        # Penalize for distractions
        if phone_detected:
            focus_score -= 20
            distractions += 1
            alert_user("mobile")

        if eyes_closed:
            alert_user("drowsy")

        if pen_detected and idle_time > 300:
            alert_user("inactivity")

        # Smooth transitions in score (no flicker)
        smooth_score = 0.85 * smooth_score + 0.15 * focus_score
        smooth_score = max(0, min(100, smooth_score))

        # --- Save focus data to JSON (every 1 second) ---
        current_time = time.time()
        if current_time - last_save_time >= 1:
            data_to_save = {
                "focus_score": round(smooth_score, 1),
                "distractions": distractions,
                "active": True,
                "timestamp": current_time
            }
            with open(json_path, "w") as f:
                json.dump(data_to_save, f)
            last_save_time = current_time

        # --- Display frame ---
        cv2.putText(frame, f"Focus Score: {int(smooth_score)}%", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 2)
        cv2.imshow("AI Focus Tracker", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Exiting Focus Session...")
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

    # Write final status
    with open(json_path, "w") as f:
        json.dump({
            "focus_score": round(smooth_score, 1),
            "distractions": distractions,
            "active": False,
            "timestamp": time.time()
        }, f)

    print("✅ Session ended and focus data saved.")


if __name__ == "__main__":
    main()

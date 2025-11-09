import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class FaceEyeTracker:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # State variables
        self.face_detected = False
        self.eyes_closed = False
        self.looking_away = False
        self.last_focus_score = 100
        self.alpha = 0.1  # smoothing factor

        # EAR calibration
        self.min_ear = 0.08
        self.max_ear = 0.35
        self.last_calibration = time.time()
        self.calibration_interval = 5
        self.EAR_FULLY_OPEN = 0.30
        self.EAR_FULLY_CLOSED = 0.18

        # FPS and thresholds
        self.FPS = 30
        self.eye_closed_start = None

        # --- NEW: Rolling window for EAR smoothing ---
        self.ear_buffer = deque(maxlen=5)  # averages over last 5 frames

    def calculate_EAR(self, landmarks, indices):
        p = np.array([[landmarks[i].x, landmarks[i].y] for i in indices])
        ear = (np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])) / (2.0 * np.linalg.norm(p[0] - p[3]))
        return ear

    def analyze_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        self.face_detected = results.multi_face_landmarks is not None

        if not self.face_detected:
            focus_score = self._smooth_score(0)
            return False, False, True, focus_score

        for face_landmarks in results.multi_face_landmarks:
            LEFT_EYE = [33, 160, 158, 133, 153, 144]
            RIGHT_EYE = [362, 385, 387, 263, 373, 380]
            left_EAR = self.calculate_EAR(face_landmarks.landmark, LEFT_EYE)
            right_EAR = self.calculate_EAR(face_landmarks.landmark, RIGHT_EYE)
            ear = (left_EAR + right_EAR) / 2.0

            # Calibration
            current_time = time.time()
            if current_time - self.last_calibration < self.calibration_interval:
                self.min_ear = min(self.min_ear, ear)
                self.max_ear = max(self.max_ear, ear)
            else:
                EAR_DIFF = self.max_ear - self.min_ear
                if EAR_DIFF > 0.05:
                    self.EAR_FULLY_CLOSED = self.min_ear * 1.15
                    self.EAR_FULLY_OPEN = self.max_ear

            # Smooth EAR and normalize
            self.ear_buffer.append(ear)
            ear_smooth = np.mean(self.ear_buffer)
            ear_range = self.EAR_FULLY_OPEN - self.EAR_FULLY_CLOSED
            eye_openness = np.clip((ear_smooth - self.EAR_FULLY_CLOSED) / (ear_range + 1e-6), 0.0, 1.0)

            # Rolling closure detection
            if not hasattr(self, "closed_buffer"):
                from collections import deque
                self.closed_buffer = deque(maxlen=10)
            self.closed_buffer.append(eye_openness < 0.25)
            closed_ratio = sum(self.closed_buffer) / len(self.closed_buffer)

            # Eyes closed if most recent frames below threshold
            if closed_ratio > 0.7:
                if not self.eyes_closed:
                    self.eye_closed_start = time.time()
                self.eyes_closed = True
            else:
                # Add small delay before declaring "open" again to prevent flicker
                if self.eyes_closed and time.time() - self.eye_closed_start < 1.0:
                    pass  # keep it closed briefly
                else:
                    self.eyes_closed = False
                    self.eye_closed_start = None

            # Debug print
            # print(f"Openness: {eye_openness:.2f}, ClosedRatio: {closed_ratio:.2f}, EyesClosed: {self.eyes_closed}")

            # Focus logic
            focus_score = self._calculate_focus(eye_openness)

        return self.face_detected, self.eyes_closed, self.looking_away, focus_score


    def _calculate_focus(self, eye_openness):
        """Maps openness and closure duration to focus score instantly."""
        # --- When eyes are closed ---
        if self.eyes_closed:
            duration = 0
            if self.eye_closed_start:
                duration = time.time() - self.eye_closed_start

            if duration > 120:
                self.last_focus_score = 25
                print("🟥 Eyes closed >2 min → Focus = 25%")
                return 25
            else:
                self.last_focus_score = 50
                print("🟠 Eyes closed detected → Focus = 50%")
                return 50

        # --- When eyes are open or partially closed ---
        if eye_openness >= 0.9:
            target = 100
        elif eye_openness >= 0.4:
            target = 75
        else:
            target = 50

        smoothed = self.alpha * target + (1 - self.alpha) * self.last_focus_score
        self.last_focus_score = smoothed
        print(f"🟢 Focus (Open) = {round(smoothed, 1)}")
        return round(smoothed, 1)


    def _smooth_score(self, new_score):
        """Applies smoothing only for gradual changes, not hard states."""
        smoothed = self.alpha * new_score + (1 - self.alpha) * self.last_focus_score
        self.last_focus_score = smoothed
        print(f"Focus Score: {round(smoothed, 1)}")  # 👈 Optional debug print
        return round(smoothed, 1)
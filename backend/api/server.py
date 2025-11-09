from fastapi import FastAPI, Response
from threading import Thread
import subprocess
import time
import psutil
import os, json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()
# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for stricter rule
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import detector modules for in-process capture. If these imports fail
# we'll fall back to launching the existing `main.py` as a subprocess.
try:
    from modules.face_eye_tracker import FaceEyeTracker
    from modules.phone_detector import PhoneDetector
    from modules.pen_tracker import PenTracker
    from modules.alerts import alert_user
    from utils.focus_score import calculate_focus_score
    import cv2
    IN_PROCESS_AVAILABLE = True
except Exception:
    IN_PROCESS_AVAILABLE = False

# Global state
focus_data = {"focus_score": 0, "distractions": 0, "active": False, "start_time": None}
process = None  # subprocess running main.py (fallback)
log_file = None  # file handle where child stdout/stderr are written


# In-process camera worker -------------------------------------------------------
class CameraWorker(Thread):
    def __init__(self, camera_index=0):
        super().__init__(daemon=True)
        self.camera_index = camera_index
        self.running = False
        self.latest_frame = None  # JPEG bytes
        self.focus_data = {"focus_score": 0, "distractions": 0, "active": False, "start_time": None}

    def run(self):
        self.running = True
        try:
            face_tracker = FaceEyeTracker()
            phone_detector = PhoneDetector()
            pen_tracker = PenTracker()
        except Exception as e:
            print("❌ CameraWorker: failed to initialize detectors:", e)
            self.running = False
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("❌ CameraWorker: could not open webcam")
            self.running = False
            return

        last_save_time = 0
        distractions = 0
        smooth_score = 100

        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "focus_data.json"))

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # Run detectors (they may draw on the frame)
            try:
                face_detected, eyes_closed, looking_away, base_score = face_tracker.analyze_frame(frame)
                phone_detected, frame = phone_detector.analyze_frame(frame)
                pen_detected, idle_time, frame = pen_tracker.analyze_frame(frame)
            except Exception as e:
                print("⚠️ Detector error:", e)
                # don't crash the worker on a single-frame error
                time.sleep(0.05)
                continue

            # Compute focus score
            try:
                focus_score = calculate_focus_score(face_detected, eyes_closed, phone_detected, pen_detected)
            except Exception:
                focus_score = 100

            if phone_detected:
                focus_score -= 20
                distractions += 1
                try:
                    alert_user("mobile")
                except Exception:
                    pass

            if eyes_closed:
                try:
                    alert_user("drowsy")
                except Exception:
                    pass

            if pen_detected and idle_time > 300:
                try:
                    alert_user("inactivity")
                except Exception:
                    pass

            smooth_score = 0.85 * smooth_score + 0.15 * focus_score
            smooth_score = max(0, min(100, smooth_score))

            # Save focus data once per second
            current_time = time.time()
            if current_time - last_save_time >= 1:
                self.focus_data = {
                    "focus_score": round(smooth_score, 1),
                    "distractions": distractions,
                    "active": True,
                    "timestamp": current_time,
                }
                try:
                    with open(json_path, "w") as f:
                        json.dump(self.focus_data, f)
                except Exception:
                    pass
                last_save_time = current_time

            # Encode frame to JPEG for streaming
            try:
                ok, jpeg = cv2.imencode('.jpg', frame)
                if ok:
                    self.latest_frame = jpeg.tobytes()
            except Exception:
                pass

            time.sleep(0.02)

        cap.release()

    def stop(self):
        self.running = False


camera_worker = None
# ----------------------------------------------------------------------------------


@app.post("/start_session")
def start_session():
    global process, log_file, camera_worker

    # If a subprocess is running already (fallback), prevent double-start
    if process is not None and process.poll() is None:
        return {"status": "error", "message": "Session already running."}

    # Prefer in-process worker when available
    if IN_PROCESS_AVAILABLE:
        if camera_worker is not None and camera_worker.running:
            return {"status": "error", "message": "Session already running (worker)."}
        camera_worker = CameraWorker(camera_index=0)
        camera_worker.start()
        print(f"✅ Started in-process CameraWorker (thread name={camera_worker.name})")
        return {"status": "success", "message": "Focus session started (in-process)."}

    # Fallback: launch main.py using the mp_env python
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    python_path = r"E:\Focus_Detection\mp_env\Scripts\python.exe"
    main_script = os.path.join(backend_dir, "main.py")

    print(f"🚀 Starting AI Focus Tracker using {python_path}")
    try:
        creation_flags = 0
        if hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            creation_flags = subprocess.CREATE_NEW_CONSOLE

        logs_dir = os.path.join(backend_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        logfile_path = os.path.join(logs_dir, "main_process.log")
        log_file = open(logfile_path, "a", buffering=1, encoding="utf-8")

        process = subprocess.Popen([
            python_path, main_script
        ], cwd=backend_dir, stdout=log_file, stderr=log_file, creationflags=creation_flags, universal_newlines=True)

        print(f"✅ Launched process PID={process.pid}; logging to {logfile_path}")
        time.sleep(0.5)
        if process.poll() is not None:
            try:
                log_file.flush()
                with open(logfile_path, "r", encoding="utf-8") as _f:
                    last = _f.read()[-2000:]
            except Exception:
                last = "(could not read log file)"
            proc_return = process.returncode
            try:
                log_file.close()
            except Exception:
                pass
            log_file = None
            process = None
            return {"status": "error", "message": "Process exited early", "code": proc_return, "log_tail": last}

    except Exception as e:
        print(f"❌ Failed to start process: {e}")
        try:
            if log_file:
                log_file.close()
        except Exception:
            pass
        log_file = None
        process = None
        return {"status": "error", "message": f"Failed to start process: {e}"}

    return {"status": "success", "message": "Focus session started."}


@app.post("/stop_session")
def stop_session():
    global process, log_file, camera_worker

    # Stop in-process worker if running
    if camera_worker is not None and camera_worker.running:
        print("🛑 Stopping in-process CameraWorker...")
        camera_worker.stop()
        camera_worker = None
        return {"status": "success", "message": "Focus session stopped (worker)."}

    if process is None or process.poll() is not None:
        return {"status": "error", "message": "No active session found."}

    print("🛑 Stopping AI Focus Tracker (subprocess)...")
    try:
        process.terminate()
        time.sleep(0.5)
        if process.poll() is None:
            process.kill()
        print(f"🗑️ Process stopped (pid={process.pid})")
    except Exception as e:
        print(f"⚠️ Error stopping process: {e}")
    finally:
        try:
            if log_file:
                log_file.close()
        except Exception:
            pass
        log_file = None
        process = None
    return {"status": "success", "message": "Focus session stopped."}


@app.get("/focus_data")
def get_focus_data():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "focus_data.json")
    json_path = os.path.abspath(json_path)

    # If the in-process worker has fresh data, prefer it
    global camera_worker
    try:
        if camera_worker is not None and camera_worker.focus_data:
            return camera_worker.focus_data
    except Exception:
        pass

    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return {"focus_score": 0, "distractions": 0, "active": False}
    return {"focus_score": 0, "distractions": 0, "active": False}


@app.get("/video_feed")
def video_feed():
    """Return an MJPEG stream of latest frames captured by the in-process worker."""
    global camera_worker
    if camera_worker is None or not camera_worker.running:
        return Response(status_code=404, content=b"No active video stream")

    def generate():
        boundary = b"--frame"
        while camera_worker is not None and camera_worker.running:
            frame = camera_worker.latest_frame
            if frame:
                yield boundary + b"\r\n"
                yield b"Content-Type: image/jpeg\r\n"
                yield b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
                yield frame + b"\r\n"
            else:
                time.sleep(0.05)

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Connection": "keep-alive"
    }

    # ✅ Use StreamingResponse instead of Response
    return StreamingResponse(
        generate(),
        headers=headers,
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
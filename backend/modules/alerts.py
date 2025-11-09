from plyer import notification
from playsound import playsound
import threading

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=4
    )

def sound_alert(sound_path="alert.mp3"):
    threading.Thread(target=lambda: playsound(sound_path)).start()

def alert_user(reason):
    if reason == "drowsy":
        show_notification("Drowsiness Alert 😴", "Eyes closed too long. Take a break!")
    elif reason == "mobile":
        show_notification("Distraction Alert 📱", "Mobile detected! Stay focused.")
    elif reason == "inactivity":
        show_notification("Break Alert ✍️", "No writing activity detected.")

import csv, time

def log_focus_data(score, face, eyes, phone, pen, moving):
    with open("focus_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            score, face, eyes, phone, pen, moving
        ])

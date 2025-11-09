def calculate_focus_score(face_detected, eyes_closed, mobile_detected, pen_detected):
    score = 100

    if not face_detected:
        score -= 40
    if eyes_closed:
        score -= 30
    if mobile_detected:
        score -= 20
    if not pen_detected:
        score -= 10

    return max(0, min(100, score))

"""Live aiming aid: shows where the card is now (green) vs the capture-day position (yellow)."""
import cv2

from camera import open_camera

TARGET = (389, 111, 1406, 960)  # card 1 on capture day: x0, y0, x1, y1
TX, TY = (TARGET[0] + TARGET[2]) / 2, (TARGET[1] + TARGET[3]) / 2
TW = TARGET[2] - TARGET[0]
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))

cap = open_camera(verbose=False)
while True:
    ok, frame = cap.read()
    if not ok:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    view = frame.copy()
    cv2.rectangle(view, TARGET[:2], TARGET[2:], (0, 255, 255), 4)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        cv2.rectangle(view, (x, y), (x + w, y + h), (0, 255, 0), 4)
        dx, dy, size = x + w / 2 - TX, y + h / 2 - TY, 100 * w / TW
        aligned = abs(dx) <= 20 and abs(dy) <= 20 and abs(size - 100) <= 2
        msg = f"dx {dx:+.0f}  dy {dy:+.0f}  size {size:.0f}%" + ("  ALIGNED" if aligned else "")
        cv2.putText(view, msg, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.8,
                    (0, 255, 0) if aligned else (0, 0, 255), 4)
    cv2.imshow("Aim  (Q = quit)", cv2.resize(view, (960, 540)))
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
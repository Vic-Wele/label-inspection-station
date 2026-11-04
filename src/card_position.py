"""Find where the label card sits: center, angle, box, and whether it fits inside the ROI."""
import cv2

from camera import open_camera
from config import ROI

cap = open_camera(verbose=False)
for _ in range(5):
    cap.read()
ok, frame = cap.read()
cap.release()

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fill the printed frame line and text
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
card = max(contours, key=cv2.contourArea)

(cx, cy), (w, h), angle = cv2.minAreaRect(card)
angle = ((angle + 45) % 90) - 45  # tilt from level, -45 to +45 degrees
x, y, bw, bh = cv2.boundingRect(card)
y0, y1, x0, x1 = ROI
inside = x >= x0 and y >= y0 and x + bw <= x1 and y + bh <= y1

print(f"center x {cx:.0f}  y {cy:.0f}   angle {angle:.1f} deg   "
      f"box x {x}-{x + bw}  y {y}-{y + bh}   in ROI: {'YES' if inside else 'NO'}")
"""Measure brightness and clipping with the locked camera settings."""
import cv2

from camera import open_camera

ROI = (380, 980, 650, 1450)  # label pocket area: y0, y1, x0, x1

cap = open_camera(verbose=False)
ok, frame = cap.read()
cap.release()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
roi = gray[ROI[0]:ROI[1], ROI[2]:ROI[3]]
clipped = (roi >= 250).mean() * 100
print(f"Whole image brightness: {gray.mean():.1f}")
print(f"Label area brightness:  {roi.mean():.1f}")
print(f"Label area clipped (pure white): {clipped:.1f}%")
cv2.imwrite("data/raw/light_check.jpg", frame)

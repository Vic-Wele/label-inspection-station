"""Capture 10 frames from the station camera and read the barcode with ROI + 2x zoom."""
import time

import cv2
import zxingcpp

from camera import open_camera
from config import ROI

N = 10
y0, y1, x0, x1 = ROI

cap = open_camera(verbose=False)
reads, times = 0, []
for i in range(N):
    ok, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    start = time.perf_counter()
    big = cv2.resize(gray[y0:y1, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    results = zxingcpp.read_barcodes(big)
    times.append((time.perf_counter() - start) * 1000)
    text = results[0].text if results else "NO READ"
    if results:
        reads += 1
    print(f"frame {i + 1}: {text}  ({times[-1]:.0f} ms)")
cap.release()

cv2.imwrite("data/raw/read_test.jpg", frame)
print(f"Read rate: {reads}/{N}   average time: {sum(times) / N:.0f} ms")
"""Capture one frame from the station camera and try to read the barcode."""
import time

import cv2
import zxingcpp

from camera import open_camera

cap = open_camera(verbose=False)
ok, frame = cap.read()
cap.release()

cv2.imwrite("data/raw/read_test.jpg", frame)
start = time.perf_counter()
results = zxingcpp.read_barcodes(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
ms = (time.perf_counter() - start) * 1000

if results:
    for r in results:
        print(f"READ: {r.text}  format: {r.format}  time: {ms:.0f} ms")
else:
    print(f"NO READ  time: {ms:.0f} ms")

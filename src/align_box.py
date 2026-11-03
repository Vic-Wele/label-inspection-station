"""Live box alignment: shows how far the box is from its position in the reference good image."""
import csv
from pathlib import Path

import cv2

from camera import open_camera

RAW = Path("data/raw")
with open(RAW / "captures.csv") as f:
    first_good = next(r for r in csv.DictReader(f) if r["class"] == "good")
ref = cv2.imread(str(RAW / first_good["file"]), cv2.IMREAD_GRAYSCALE)
TPL = ref[300:470, 920:1100]  # 3M stamp

cap = open_camera(verbose=False)
while True:
    ok, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray, TPL, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(res)
    dx, dy = x - 920, y - 300
    good = abs(dx) <= 5 and abs(dy) <= 5 and score > 0.7
    color = (0, 255, 0) if good else (0, 0, 255)
    view = cv2.resize(frame, (960, 540))
    cv2.putText(view, f"dx={dx:+d}  dy={dy:+d}  match={score:.2f}  {'ALIGNED' if good else 'MOVE BOX'}",
                (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(view, "dx>0: move box LEFT   dy>0: move box UP   Q=quit",
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.imshow("Align box", view)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

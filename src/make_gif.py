"""Build a README demo GIF from the latest FAT run: each placement with a PASS/FAIL banner and the reason."""
import csv
from pathlib import Path

import cv2
from PIL import Image

FAT = Path("data/fat")
log = sorted(FAT.glob("fat_*.csv"))[-1]
rows = list(csv.DictReader(open(log)))

frames = []
for r in rows:
    if r["class"] == "missing" and r["step"] != "2":
        continue  # keep just one empty-dip example
    img = cv2.resize(cv2.imread(str(FAT / r["image"])), (640, 360))
    passed = r["result"] == "PASS"
    color = (0, 160, 0) if passed else (0, 0, 210)

    cv2.rectangle(img, (0, 0), (640, 46), color, -1)
    cv2.putText(img, f"{r['result']}   {r['reason']}", (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    score = "-" if r["reason"] == "NO CARD" else f"{float(r['score']):.2f}"
    what = "missing label" if r["class"] == "missing" else r["class"].replace("_", " ")
    cv2.rectangle(img, (0, 324), (640, 360), (40, 40, 40), -1)
    cv2.putText(img, f"{what}  |  score {score}  |  {r['cycle_ms']} ms", (12, 348),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    frames.append(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))

out = Path("media/demo.gif")
frames[0].save(out, save_all=True, append_images=frames[1:], duration=1400, loop=0, optimize=True)
print(f"{len(frames)} frames from {log.name} -> {out} ({out.stat().st_size / 1e6:.1f} MB)")
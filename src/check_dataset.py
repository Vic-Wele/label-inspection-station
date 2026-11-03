"""Check every captured image: barcode matches the logged ID, and brightness is consistent."""
import csv
import statistics
import sys
from pathlib import Path

import cv2
import zxingcpp

from config import ROI

if ROI is None:
    sys.exit("ROI is not set in config.py yet (step 4i).")

RAW = Path("data/raw")
wanted = sys.argv[1] if len(sys.argv) > 1 else None

with open(RAW / "captures.csv") as f:
    rows = [r for r in csv.DictReader(f) if wanted is None or r["class"] == wanted]

y0, y1, x0, x1 = ROI
means, problems = [], []
for r in rows:
    img = cv2.imread(str(RAW / r["file"]), cv2.IMREAD_GRAYSCALE)
    if img is None:
        problems.append((r["file"], "file missing"))
        continue
    means.append(img.mean())
    roi = img[y0:y1, x0:x1]
    big = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    reads = zxingcpp.read_barcodes(big)
    text = reads[0].text if reads else "NO READ"
    if text != r["label_id"]:
        problems.append((r["file"], f"read {text}, expected {r['label_id']}"))

print(f"Images checked: {len(rows)}")
print(f"Brightness: mean {statistics.mean(means):.1f}, min {min(means):.1f}, max {max(means):.1f}")
print(f"Barcode problems: {len(problems)}")
for name, why in problems:
    print("  ", name, "->", why)
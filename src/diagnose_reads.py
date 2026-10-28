"""Compare barcode read methods on the captured good images."""
import csv
from pathlib import Path

import cv2
import zxingcpp

RAW = Path("data/raw")
ROI = (380, 980, 650, 1450)  # y0, y1, x0, x1: generous box around the label pocket

with open(RAW / "captures.csv") as f:
    rows = [r for r in csv.DictReader(f) if r["class"] == "good"]


def read(img, **kw):
    res = zxingcpp.read_barcodes(img, **kw)
    return res[0].text if res else None


methods = {
    "1 full image (default)": lambda im: read(im),
    "2 full image, no downscale": lambda im: read(im, try_downscale=False),
    "3 label area only (ROI)": lambda im: read(im[ROI[0]:ROI[1], ROI[2]:ROI[3]]),
    "4 ROI enlarged 2x": lambda im: read(cv2.resize(im[ROI[0]:ROI[1], ROI[2]:ROI[3]], None,
                                                   fx=2, fy=2, interpolation=cv2.INTER_CUBIC)),
}
scores = {name: 0 for name in methods}
brightest = (0, "")
for r in rows:
    img = cv2.imread(str(RAW / r["file"]), cv2.IMREAD_GRAYSCALE)
    brightest = max(brightest, (img.mean(), r["file"]))
    for name, fn in methods.items():
        scores[name] += fn(img) == r["label_id"]

for name, score in scores.items():
    print(f"{name:30} {score}/{len(rows)} read correctly")
print(f"Brightest image: {brightest[1]} (mean {brightest[0]:.1f})")

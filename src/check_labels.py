"""Decode every generated label digitally to verify the barcodes before printing."""
import csv

import zxingcpp

from make_labels import make_label, fade, break_barcode

with open("labels/manifest.csv") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    img, box = make_label(r["label_id"], r["lot"])
    if r["intended_class"] == "faded":
        img = fade(img)
    if r["intended_class"] == "damaged_barcode":
        img = break_barcode(img, box)
    results = zxingcpp.read_barcodes(img)
    text = results[0].text if results else "NO READ"
    ok = "OK " if text == r["label_id"] else "-- "
    print(f"{ok} {r['label_id']:10} {r['intended_class']:22} read: {text}")

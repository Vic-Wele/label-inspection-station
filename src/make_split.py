"""Split images by card: train / threshold / test. Writes data/split.csv."""
import csv
from collections import Counter
from pathlib import Path

RAW = Path("data/raw")
TRAIN_CARDS = range(1, 12)       # good cards 1 to 11
THRESHOLD_CARDS = range(12, 16)  # good cards 12 to 15
# good cards 16 to 19 and every defect image go to test

with open(RAW / "captures.csv") as f:
    rows = list(csv.DictReader(f))

out = []
for r in rows:
    if r["class"] == "good":
        card = int(r["label_id"].split("-")[1])
        if card in TRAIN_CARDS:
            split = "train"
        elif card in THRESHOLD_CARDS:
            split = "threshold"
        else:
            split = "test"
        defect = 0
    else:
        split = "test"
        defect = 1
    out.append({"file": r["file"], "label_id": r["label_id"], "class": r["class"],
                "split": split, "defect": defect})

with open("data/split.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["file", "label_id", "class", "split", "defect"])
    w.writeheader()
    w.writerows(out)

counts = Counter((o["split"], o["class"]) for o in out)
for (split, cls), n in sorted(counts.items()):
    print(f"{split:<10} {cls:<16} {n}")
print("Total:", len(out))
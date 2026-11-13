"""Train the PatchCore-style model on straightened card crops, set the threshold, and test.

Uses inspector.py for every check, so training, live runs and the FAT all use the same logic.
Threshold: highest score among the good threshold images (no peeking at defects).
"""
import csv
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch

from inspector import MAX_SKEW_DEG, MODEL_PATH, SIZE, features, inspect_gray, patch_scores
from locate import straight_crop

RAW = Path("data/raw")
HEAT = Path("data/processed/heatmaps")
HEAT.mkdir(parents=True, exist_ok=True)
Path("models").mkdir(exist_ok=True)
BANK_KEEP = 0.10  # keep 10% of good patches in the memory bank
torch.manual_seed(0)


def load_gray(file):
    return cv2.imread(str(RAW / file), cv2.IMREAD_GRAYSCALE)


def greedy_coreset(feats, n):
    """Pick n patches, each time adding the one farthest from all picked so far."""
    z = feats @ (torch.randn(feats.shape[1], 128) / 128 ** 0.5)  # random projection for speed
    picked = [0]
    dmin = torch.cdist(z, z[0:1]).squeeze(1)
    for _ in range(n - 1):
        i = int(torch.argmax(dmin))
        picked.append(i)
        dmin = torch.minimum(dmin, torch.cdist(z, z[i:i + 1]).squeeze(1))
    return feats[picked]


with open("data/split.csv") as f:
    rows = list(csv.DictReader(f))
by_split = defaultdict(list)
for r in rows:
    by_split[r["split"]].append(r)

# 1. Train: memory bank from straightened good train crops
t0 = time.perf_counter()
all_feats = torch.cat([features(straight_crop(load_gray(r["file"]))[0])[0] for r in by_split["train"]])
bank = greedy_coreset(all_feats, int(len(all_feats) * BANK_KEEP))
print(f"Trained on {len(by_split['train'])} images, bank {len(bank)} of {len(all_feats)} patches, "
      f"{time.perf_counter() - t0:.1f} s")

# 2. Threshold: highest score among good threshold crops
thr_scores = [patch_scores(features(straight_crop(load_gray(r["file"]))[0])[0], bank).max().item()
              for r in by_split["threshold"]]
thr = max(thr_scores)
print(f"Threshold scores: min {min(thr_scores):.3f}, max {thr:.3f}  ->  threshold {thr:.3f}"
      f"   (skew limit {MAX_SKEW_DEG} deg)")
torch.save({"bank": bank, "threshold": thr, "size": SIZE, "crop": "straight_card"}, MODEL_PATH)

# 3. Test with the shared inspect function
results, ms = [], []
for r in by_split["test"]:
    gray = load_gray(r["file"])
    start = time.perf_counter()
    out = inspect_gray(gray, bank, thr)
    ms.append((time.perf_counter() - start) * 1000)

    reader_fail = out["barcode"] != r["label_id"]
    rule_fail = out["skewed"]
    model_fail = out["score"] > thr
    results.append({**r, "score": round(out["score"], 3), "angle": "" if out["angle"] is None else round(out["angle"], 1),
                    "read": out["barcode"], "reader_fail": int(reader_fail), "rule_fail": int(rule_fail),
                    "model_fail": int(model_fail), "fail": int(not out["passed"]), "reason": out["reason"]})

    if out["crop"] is not None:
        crop = out["crop"]
        pmap = cv2.resize(out["pmap"], (crop.shape[1], crop.shape[0]))
        norm = np.clip(pmap / (2 * thr) * 255, 0, 255).astype(np.uint8)
        over = cv2.addWeighted(cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR), 0.6,
                               cv2.applyColorMap(norm, cv2.COLORMAP_JET), 0.4, 0)
        cv2.imwrite(str(HEAT / f"{r['class']}_{Path(r['file']).stem}.jpg"), over)

with open("data/processed/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)

# 4. Summary
print(f"\n{'class':<16}{'n':>4}{'reader':>8}{'skew':>6}{'model':>7}{'all':>5}   score min-max")
for cls in sorted({r["class"] for r in results}):
    rs = [r for r in results if r["class"] == cls]
    sc = [r["score"] for r in rs]
    print(f"{cls:<16}{len(rs):>4}{sum(r['reader_fail'] for r in rs):>8}{sum(r['rule_fail'] for r in rs):>6}"
          f"{sum(r['model_fail'] for r in rs):>7}{sum(r['fail'] for r in rs):>5}   {min(sc):.3f}-{max(sc):.3f}")

good = [r for r in results if r["defect"] == "0"]
bad = [r for r in results if r["defect"] == "1"]
print(f"\nFalse reject rate (good flagged): {sum(r['fail'] for r in good)}/{len(good)}")
print(f"Detection rate (defects flagged): {sum(r['fail'] for r in bad)}/{len(bad)}")
print(f"Average time per image (locate + straighten + model + barcode): {sum(ms) / len(ms):.0f} ms")
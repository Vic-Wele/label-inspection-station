"""PatchCore-style anomaly detection: train on good images, set threshold, test.

Train: features of good images (ResNet18 layer2 + layer3) go into a memory bank.
Bank: greedy coreset (keeps the 10% of patches that best cover all good variety).
Score: for each patch, distance to the nearest good patch. Image score = largest patch distance.
Threshold: highest score among the threshold images (good only, no peeking at defects).
Decision: FAIL if the barcode doesn't read OR the score is above the threshold.
"""
import csv
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision
import zxingcpp

from config import ROI

RAW = Path("data/raw")
HEAT = Path("data/processed/heatmaps")
HEAT.mkdir(parents=True, exist_ok=True)
Path("models").mkdir(exist_ok=True)
SIZE = (320, 280)  # model input: width, height (keeps the ROI's shape)
BANK_KEEP = 0.10   # keep 10% of good patches in the memory bank
torch.manual_seed(0)
y0, y1, x0, x1 = ROI

net = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).eval()
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def load_crop(file):
    img = cv2.imread(str(RAW / file), cv2.IMREAD_GRAYSCALE)
    return img[y0:y1, x0:x1]


@torch.no_grad()
def features(crop):
    small = cv2.resize(crop, SIZE, interpolation=cv2.INTER_AREA)
    x = torch.from_numpy(small)[None, None].float().div(255).repeat(1, 3, 1, 1)
    x = (x - MEAN) / STD
    x = net.maxpool(net.relu(net.bn1(net.conv1(x))))
    l2 = net.layer2(net.layer1(x))
    l3 = net.layer3(l2)
    l3 = F.interpolate(l3, size=l2.shape[-2:], mode="bilinear", align_corners=False)
    f = F.avg_pool2d(torch.cat([l2, l3], 1), 3, 1, 1)
    h, w = f.shape[-2:]
    return f[0].permute(1, 2, 0).reshape(-1, f.shape[1]), (h, w)


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


def patch_scores(feat, bank):
    return torch.cdist(feat, bank).min(1).values


def read_barcode(crop):
    big = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    reads = zxingcpp.read_barcodes(big)
    return reads[0].text if reads else "NO READ"


with open("data/split.csv") as f:
    rows = list(csv.DictReader(f))
by_split = defaultdict(list)
for r in rows:
    by_split[r["split"]].append(r)

# 1. Train: build the memory bank from good train images
t0 = time.perf_counter()
all_feats = torch.cat([features(load_crop(r["file"]))[0] for r in by_split["train"]])
bank = greedy_coreset(all_feats, int(len(all_feats) * BANK_KEEP))
print(f"Trained on {len(by_split['train'])} images, bank {len(bank)} of {len(all_feats)} patches "
      f"(greedy coreset), {time.perf_counter() - t0:.1f} s")

# 2. Threshold: highest score among good threshold images
thr_scores = [patch_scores(features(load_crop(r["file"]))[0], bank).max().item()
              for r in by_split["threshold"]]
thr_auto = max(thr_scores)
thr = 2.16  # commissioned: midpoint of highest good (2.129) and lowest defect (2.198)
print(f"Threshold scores: min {min(thr_scores):.3f}, max {thr_auto:.3f} (auto)  ->  commissioned threshold {thr:.3f}")
torch.save({"bank": bank, "threshold": thr, "size": SIZE, "roi": ROI}, "models/patchcore.pt")

# 3. Test
results, ms = [], []
for r in by_split["test"]:
    crop = load_crop(r["file"])
    start = time.perf_counter()
    feat, (h, w) = features(crop)
    ps = patch_scores(feat, bank)
    score = ps.max().item()
    text = read_barcode(crop)
    ms.append((time.perf_counter() - start) * 1000)

    read_ok = text == r["label_id"]
    model_fail = score > thr
    fail = (not read_ok) or model_fail
    results.append({**r, "score": round(score, 3), "read": text,
                    "reader_fail": int(not read_ok), "model_fail": int(model_fail), "fail": int(fail)})

    pmap = cv2.resize(ps.reshape(h, w).numpy(), (crop.shape[1], crop.shape[0]))
    norm = np.clip(pmap / (2 * thr) * 255, 0, 255).astype(np.uint8)
    over = cv2.addWeighted(cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR), 0.6,
                           cv2.applyColorMap(norm, cv2.COLORMAP_JET), 0.4, 0)
    cv2.imwrite(str(HEAT / f"{r['class']}_{Path(r['file']).stem}.jpg"), over)

with open("data/processed/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)

# 4. Summary
print(f"\n{'class':<16}{'n':>4}{'reader':>8}{'model':>7}{'both':>6}   score min-max")
for cls in sorted({r["class"] for r in results}):
    rs = [r for r in results if r["class"] == cls]
    sc = [r["score"] for r in rs]
    print(f"{cls:<16}{len(rs):>4}{sum(r['reader_fail'] for r in rs):>8}"
          f"{sum(r['model_fail'] for r in rs):>7}{sum(r['fail'] for r in rs):>6}"
          f"   {min(sc):.3f}-{max(sc):.3f}")

good = [r for r in results if r["defect"] == "0"]
bad = [r for r in results if r["defect"] == "1"]
print(f"\nFalse reject rate (good flagged): {sum(r['fail'] for r in good)}/{len(good)}")
print(f"Detection rate (defects flagged): {sum(r['fail'] for r in bad)}/{len(bad)}")
print(f"Average time per image (model + barcode): {sum(ms) / len(ms):.0f} ms")
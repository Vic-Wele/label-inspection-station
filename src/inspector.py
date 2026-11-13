"""Shared inspection logic, used by train_eval.py, live.py and fat.py so they never drift apart.

Locate and straighten the card, then 4 checks (any one fails the part):
  1. NO CARD   - no card found
  2. SKEWED    - card tilted more than MAX_SKEW_DEG (a rule, measured in degrees)
  3. NO READ   - barcode doesn't read
  4. ANOMALY   - model score above the threshold (appearance: tears, smudges, fading)
"""
import cv2
import torch
import torch.nn.functional as F
import torchvision
import zxingcpp

from locate import straight_crop

SIZE = (320, 280)      # model input: width, height
MAX_SKEW_DEG = 3.0     # set from data: good cards 0 to 1.9 deg, skewed defects 4.6 to 8.9 deg
NO_CARD_SCORE = 99.0
MODEL_PATH = "models/patchcore.pt"

net = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).eval()
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


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


def patch_scores(feat, bank):
    return torch.cdist(feat, bank).min(1).values


def read_barcode(crop):
    reads = zxingcpp.read_barcodes(crop)
    return reads[0].text if reads else "NO READ"


def load_model(path=MODEL_PATH):
    m = torch.load(path, weights_only=True)
    return m["bank"], m["threshold"]


def inspect_gray(gray, bank, thr):
    """Inspect one grayscale image. Returns a dict with the decision and the details."""
    crop, angle = straight_crop(gray)
    if crop is None:
        return {"passed": False, "reason": "NO CARD", "barcode": "NO CARD", "score": NO_CARD_SCORE,
                "angle": None, "skewed": False, "crop": None, "pmap": None}
    feat, (h, w) = features(crop)
    ps = patch_scores(feat, bank)
    score = ps.max().item()
    text = read_barcode(crop)
    skewed = abs(angle) > MAX_SKEW_DEG

    reasons = []
    if skewed:
        reasons.append(f"SKEWED {angle:+.1f} deg")
    if not text.startswith("PKG-"):
        reasons.append("NO READ")
    if score > thr:
        reasons.append("ANOMALY")
    return {"passed": not reasons, "reason": ", ".join(reasons) or "OK", "barcode": text, "score": score,
            "angle": angle, "skewed": skewed, "crop": crop, "pmap": ps.reshape(h, w).numpy()}
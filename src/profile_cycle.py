"""Time each stage of one inspection on a saved image (10 runs each), to find what's slow."""
import time

import cv2
import zxingcpp

from inspector import features, load_model, patch_scores
from locate import find_card_contour, straight_crop

IMG = "data/fat/20261112_224201_step01_PASS.png"
gray = cv2.imread(IMG, cv2.IMREAD_GRAYSCALE)
bank, thr = load_model()


def timed(name, fn, n=10):
    fn()  # warm-up
    t0 = time.perf_counter()
    for _ in range(n):
        out = fn()
    print(f"{name:<28} {(time.perf_counter() - t0) / n * 1000:6.1f} ms")
    return out


timed("find card (contour)", lambda: find_card_contour(gray))
crop, _ = timed("straighten + crop", lambda: straight_crop(gray))
feat, _ = timed("model features", lambda: features(crop))
timed("model scoring", lambda: patch_scores(feat, bank).max().item())
big = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
r2 = timed("barcode read, 2x zoom", lambda: zxingcpp.read_barcodes(cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)))
r1 = timed("barcode read, 1x (no zoom)", lambda: zxingcpp.read_barcodes(crop))
print("2x read:", r2[0].text if r2 else "NO READ", "   1x read:", r1[0].text if r1 else "NO READ")
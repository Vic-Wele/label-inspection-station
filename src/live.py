"""Live inspection loop: hand in beam -> hand out AND scene still -> capture -> locate card -> barcode + model -> PLC light -> log.

PASS = card found AND barcode reads AND anomaly score <= threshold. Press Q in the preview to quit.
"""
import csv
import time
from datetime import datetime
from pathlib import Path

import cv2
import torch
import torch.nn.functional as F
import torchvision
import zxingcpp
from pymodbus.client import ModbusSerialClient

from camera import open_camera
from locate import card_crop

PORT = "COM4"
PASS_COIL, FAIL_COIL, BEAM_INPUT = 3, 0, 0  # %QX0.3, %QX0.0, %IX0.0
SETTLE_S = 0.5    # beam clear AND scene still for this long before inspecting
MOTION_MAX = 3.0  # average pixel change between frames; above this = something is moving
LIVE = Path("data/live")
LIVE.mkdir(parents=True, exist_ok=True)
LOG = LIVE / "log.csv"

m = torch.load("models/patchcore.pt", weights_only=True)
bank, thr, SIZE = m["bank"], m["threshold"], tuple(m["size"])

# Same feature extractor as train_eval.py (must match exactly)
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
    return f[0].permute(1, 2, 0).reshape(-1, f.shape[1])


def inspect(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    crop = card_crop(gray)
    if crop is None:
        return False, "NO CARD", 99.0, gray
    score = torch.cdist(features(crop), bank).min(1).values.max().item()
    big = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    reads = zxingcpp.read_barcodes(big)
    text = reads[0].text if reads else "NO READ"
    passed = text.startswith("PKG-") and score <= thr
    return passed, text, score, gray


client = ModbusSerialClient(port=PORT, baudrate=115200, timeout=1)
print("PLC connected:", client.connect())


def beam_clear():
    r = client.read_discrete_inputs(BEAM_INPUT, count=1, device_id=1)
    return None if r.isError() else r.bits[0]


def lights(passed, failed):
    client.write_coil(PASS_COIL, passed, device_id=1)
    client.write_coil(FAIL_COIL, failed, device_id=1)


new_log = not LOG.exists()
log_file = open(LOG, "a", newline="")
log = csv.writer(log_file)
if new_log:
    log.writerow(["time", "result", "barcode", "score", "threshold", "cycle_ms", "image"])

lights(False, False)
cap = open_camera(verbose=False)
ok, frame = cap.read()
inspect(frame)  # warm-up run so the first real inspection is fast
print(f"Ready. Threshold {thr:.3f}. Place a card (hand breaks the beam), then take your hand out.")

state, t_still, last = "wait_hand", 0.0, "Ready"
last_color = (255, 255, 255)
prev_small, motion = None, 99.0
try:
    while True:
        ok, frame = cap.read()
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (160, 90))
        if prev_small is not None:
            motion = cv2.absdiff(small, prev_small).mean()
        prev_small = small
        clear = beam_clear()

        if state == "wait_hand" and clear is False:
            lights(False, False)
            state, last, last_color = "hand_in", "Loading...", (255, 255, 255)
        elif state == "hand_in" and clear is True:
            state, t_still = "settling", time.perf_counter()
        elif state == "settling":
            if clear is False:
                state = "hand_in"
            elif motion > MOTION_MAX:
                t_still = time.perf_counter()  # something is still moving: restart the wait
            elif time.perf_counter() - t_still >= SETTLE_S:
                t0 = time.perf_counter()
                cap.grab()
                ok, frame = cap.read()  # fresh frame taken after the scene settled
                passed, text, score, gray = inspect(frame)
                lights(passed, not passed)
                ms = (time.perf_counter() - t0) * 1000

                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result = "PASS" if passed else "FAIL"
                name = f"{stamp}_{result}.png"
                cv2.imwrite(str(LIVE / name), gray)
                log.writerow([stamp, result, text, f"{score:.3f}", f"{thr:.3f}", f"{ms:.0f}", name])
                log_file.flush()

                last = f"{result}  {text}  score {score:.2f} (thr {thr:.2f})  {ms:.0f} ms"
                last_color = (0, 200, 0) if passed else (0, 0, 255)
                print(last)
                state = "wait_hand"

        view = cv2.resize(frame, (960, 540))
        cv2.putText(view, last, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, last_color, 2)
        cv2.putText(view, f"state: {state}   motion {motion:.1f}   Q = quit", (10, 520),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("Live inspection", view)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    lights(False, False)
    cap.release()
    client.close()
    log_file.close()
    cv2.destroyAllWindows()
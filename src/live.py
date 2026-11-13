"""Live inspection loop: hand in beam -> hand out AND scene still -> capture -> inspect -> PLC light -> log.

All checks come from inspector.py (no card, skew, barcode, anomaly). Press Q in the preview to quit.
"""
import csv
import time
from datetime import datetime
from pathlib import Path

import cv2
from pymodbus.client import ModbusSerialClient

from camera import open_camera
from inspector import inspect_gray, load_model

PORT = "COM4"
PASS_COIL, FAIL_COIL, BEAM_INPUT = 3, 0, 0  # %QX0.3, %QX0.0, %IX0.0
SETTLE_S = 0.5    # beam clear AND scene still for this long before inspecting
MOTION_MAX = 3.0  # average pixel change between frames; above this = something is moving
LIVE = Path("data/live")
LIVE.mkdir(parents=True, exist_ok=True)
LOG = LIVE / "log.csv"

bank, thr = load_model()
client = ModbusSerialClient(port=PORT, baudrate=115200, timeout=1)
print("PLC connected:", client.connect())


def beam_clear():
    r = client.read_discrete_inputs(BEAM_INPUT, count=1, device_id=1)
    return None if r.isError() else r.bits[0]


def lights(passed, failed):
    client.write_coils(0, [failed, False, False, passed], device_id=1)  # coils 0-3: fail_flag, green, red, pass_flag


new_log = not LOG.exists()
log_file = open(LOG, "a", newline="")
log = csv.writer(log_file)
if new_log:
    log.writerow(["time", "result", "reason", "barcode", "score", "angle", "threshold", "cycle_ms", "image"])

lights(False, False)
cap = open_camera(verbose=False)
ok, frame = cap.read()
inspect_gray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), bank, thr)  # warm-up
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
                t_still = time.perf_counter()
            elif time.perf_counter() - t_still >= SETTLE_S:
                t0 = time.perf_counter()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                out = inspect_gray(gray, bank, thr)
                lights(out["passed"], not out["passed"])
                ms = (time.perf_counter() - t0) * 1000

                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result = "PASS" if out["passed"] else "FAIL"
                name = f"{stamp}_{result}.png"
                cv2.imwrite(str(LIVE / name), gray)
                angle = "" if out["angle"] is None else f"{out['angle']:.1f}"
                log.writerow([stamp, result, out["reason"], out["barcode"], f"{out['score']:.3f}", angle,
                              f"{thr:.3f}", f"{ms:.0f}", name])
                log_file.flush()

                last = f"{result}  {out['reason']}  {out['barcode']}  score {out['score']:.2f}  {ms:.0f} ms"
                last_color = (0, 200, 0) if out["passed"] else (0, 0, 255)
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
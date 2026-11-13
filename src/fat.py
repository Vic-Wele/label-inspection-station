"""Guided FAT run: the station tells the operator what to do, inspects, and compares expected vs actual.

All checks come from inspector.py. Every placement is followed by a removal (an empty-dip, missing-label test).
Results go to data/fat/, with a summary at the end. Press Q to stop early.
"""
import csv
import statistics
import time
from datetime import datetime
from pathlib import Path

import cv2
from pymodbus.client import ModbusSerialClient

from camera import open_camera
from inspector import inspect_gray, load_model

PORT = "COM4"
PASS_COIL, FAIL_COIL, BEAM_INPUT = 3, 0, 0
SETTLE_S, MOTION_MAX = 0.5, 3.0
OUT = Path("data/fat")
OUT.mkdir(parents=True, exist_ok=True)

PLACEMENTS = [
    ("card 16", "good"), ("card 27 (faded)", "faded"), ("card 17", "good"),
    ("card 29 (damaged barcode)", "damaged_barcode"), ("card 18", "good"), ("card 20 (torn)", "torn"),
    ("card 19", "good"), ("card 23 (smudged)", "smudged"), ("card 16", "good"),
    ("card 25 (scratched)", "scratched"), ("card 17", "good"),
    ("card 1 SKEWED: flat on top, top edge lifted about 2 cm", "skewed"),
    ("card 18", "good"), ("card 19", "good"),
]
PLAN = []
for what, cls in PLACEMENTS:
    PLAN.append((f"Place {what}", cls, "PASS" if cls == "good" else "FAIL"))
    PLAN.append(("Remove the card (empty dip)", "missing", "FAIL"))

bank, thr = load_model()
client = ModbusSerialClient(port=PORT, baudrate=115200, timeout=1)
print("PLC connected:", client.connect())


def beam_clear():
    r = client.read_discrete_inputs(BEAM_INPUT, count=1, device_id=1)
    return None if r.isError() else r.bits[0]


def lights(passed, failed):
    client.write_coils(0, [failed, False, False, passed], device_id=1)  # coils 0-3: fail_flag, green, red, pass_flag


stamp0 = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = OUT / f"fat_{stamp0}.csv"
log_file = open(log_path, "w", newline="")
log = csv.writer(log_file)
log.writerow(["step", "instruction", "class", "expected", "result", "ok", "reason", "barcode", "score",
              "angle", "cycle_ms", "image"])

lights(False, False)
cap = open_camera(verbose=False)
ok, frame = cap.read()
inspect_gray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), bank, thr)  # warm-up
print(f"FAT start. Threshold {thr:.3f}. {len(PLAN)} steps.")
print(f"Step 1: {PLAN[0][0]}")

step, rows = 0, []
state, t_still, prev_small, motion = "wait_hand", 0.0, None, 99.0
try:
    while step < len(PLAN):
        ok, frame = cap.read()
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (160, 90))
        if prev_small is not None:
            motion = cv2.absdiff(small, prev_small).mean()
        prev_small = small
        clear = beam_clear()

        if state == "wait_hand" and clear is False:
            lights(False, False)
            state = "hand_in"
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

                instruction, cls, expected = PLAN[step]
                result = "PASS" if out["passed"] else "FAIL"
                good = result == expected
                name = f"{stamp0}_step{step + 1:02d}_{result}.png"
                cv2.imwrite(str(OUT / name), gray)
                angle = "" if out["angle"] is None else f"{out['angle']:.1f}"
                row = [step + 1, instruction, cls, expected, result, int(good), out["reason"], out["barcode"],
                       f"{out['score']:.3f}", angle, f"{ms:.0f}", name]
                log.writerow(row)
                log_file.flush()
                rows.append(row)
                print(f"Step {step + 1}: {result} (expected {expected}) {'OK' if good else '<-- MISMATCH'}  "
                      f"{out['reason']}  {out['barcode']}  score {out['score']:.2f}  angle {angle}  {ms:.0f} ms")
                step += 1
                if step < len(PLAN):
                    print(f"Step {step + 1}: {PLAN[step][0]}")
                state = "wait_hand"

        view = cv2.resize(frame, (960, 540))
        msg = PLAN[step][0] if step < len(PLAN) else "Done"
        cv2.putText(view, f"Step {min(step + 1, len(PLAN))}/{len(PLAN)}: {msg}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(view, f"state: {state}   motion {motion:.1f}   Q = stop", (10, 520),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("FAT", view)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    lights(False, False)
    cap.release()
    client.close()
    log_file.close()
    cv2.destroyAllWindows()


def count(cls_filter):
    rs = [r for r in rows if cls_filter(r[2])]
    return sum(r[5] for r in rs), len(rs)


g_ok, g_n = count(lambda c: c == "good")
d_ok, d_n = count(lambda c: c not in ("good", "missing"))
m_ok, m_n = count(lambda c: c == "missing")
card_times = [int(r[10]) for r in rows if r[2] != "missing"]
print("\n===== FAT summary =====")
print(f"Good passed:          {g_ok}/{g_n}   (false rejects: {g_n - g_ok})")
print(f"Defects caught:       {d_ok}/{d_n}")
print(f"Missing caught:       {m_ok}/{m_n}")
if card_times:
    print(f"Cycle time (cards):   mean {statistics.mean(card_times):.0f} ms, max {max(card_times)} ms (limit 500)")
print(f"Log: {log_path}")
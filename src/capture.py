"""Guided image capture: shows which card to place, saves grayscale PNGs, and logs every shot.

Example: python src/capture.py --set good --ids 1-26 --shots 4
For a missing label: python src/capture.py --set missing --ids none --shots 5
"""
import argparse
import csv
from datetime import datetime
from pathlib import Path

import cv2

from camera import open_camera

RAW = Path("data/raw")
LOG = RAW / "captures.csv"


def parse_ids(text):
    if text == "none":
        return ["NONE"]
    start, end = (int(x) for x in text.split("-"))
    return [f"PKG-{i:04d}" for i in range(start, end + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, help="class name, for example good or faded")
    ap.add_argument("--ids", required=True, help="range like 1-26, or none")
    ap.add_argument("--shots", type=int, default=4)
    args = ap.parse_args()

    out_dir = RAW / args.set
    out_dir.mkdir(parents=True, exist_ok=True)
    new_log = not LOG.exists()
    log_file = open(LOG, "a", newline="")
    log = csv.writer(log_file)
    if new_log:
        log.writerow(["file", "label_id", "class", "shot", "timestamp"])

    cam = open_camera(verbose=False)
    jobs = [(i, s) for i in parse_ids(args.ids) for s in range(1, args.shots + 1)]
    n = 0
    while n < len(jobs):
        label_id, shot = jobs[n]
        ok, frame = cam.read()
        if not ok:
            print("Camera read failed")
            break
        view = cv2.resize(frame, (960, 540))
        msg = f"{args.set}: {label_id}  shot {shot}/{args.shots}  ({n + 1}/{len(jobs)})  SPACE=capture  Q=quit"
        cv2.putText(view, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Capture", view)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{label_id}_s{shot}_{stamp}.png"
            cv2.imwrite(str(out_dir / name), gray)
            log.writerow([f"{args.set}/{name}", label_id, args.set, shot, stamp])
            log_file.flush()
            print("Saved", name)
            n += 1
    cam.release()
    log_file.close()
    cv2.destroyAllWindows()
    print(f"Done: {n} of {len(jobs)} captured into {out_dir}")


if __name__ == "__main__":
    main()

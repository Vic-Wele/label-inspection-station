"""Open the station camera with locked settings and run a startup self-check."""
import cv2

from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAMERA_SETTINGS

# The Windows driver reports these on/off switches with its own codes, so we don't compare them.
SWITCHES = {"autofocus off", "auto exposure off", "auto white balance off"}


def apply_settings(cap):
    for name, prop, value in CAMERA_SETTINGS:
        cap.set(prop, value)


def open_camera(verbose=True):
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    apply_settings(cap)
    for _ in range(10):  # let the camera settle
        cap.read()
    apply_settings(cap)  # second pass: some webcams ignore focus until streaming
    for _ in range(5):
        cap.read()

    problems = 0
    if verbose:
        print(f"{'setting':24} {'want':>8} {'got':>8}")
    for name, prop, value in CAMERA_SETTINGS:
        if name in SWITCHES:
            continue
        got = cap.get(prop)
        bad = abs(got - value) >= 0.01
        problems += bad
        if verbose:
            print(f"{name:24} {value:>8} {got:>8}{'  <-- MISMATCH' if bad else ''}")
    print("Camera self-check:", "PASS" if problems == 0 else f"FAIL ({problems} settings)")
    return cap


if __name__ == "__main__":
    cam = open_camera()
    ok, frame = cam.read()
    cam.release()
    cv2.imwrite("data/raw/locked_settings_test.jpg", frame)
    print("Saved data/raw/locked_settings_test.jpg")

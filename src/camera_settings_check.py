"""Check that the USB webcam accepts full HD and manual focus/exposure."""
import cv2

CAM_INDEX = 1  # USB webcam

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

print("Autofocus off accepted:", cap.set(cv2.CAP_PROP_AUTOFOCUS, 0))
print("Focus set accepted:    ", cap.set(cv2.CAP_PROP_FOCUS, 30))
print("Exposure set accepted: ", cap.set(cv2.CAP_PROP_EXPOSURE, -6))

for _ in range(10):  # let the camera settle
    cap.read()

ok, frame = cap.read()
print("Frame read:", ok)
if ok:
    h, w = frame.shape[:2]
    print(f"Actual resolution: {w}x{h}")
    cv2.imwrite("data/raw/camera_settings_test.jpg", frame)
    print("Saved data/raw/camera_settings_test.jpg")

print("Readback -> autofocus:", cap.get(cv2.CAP_PROP_AUTOFOCUS),
      "focus:", cap.get(cv2.CAP_PROP_FOCUS),
      "exposure:", cap.get(cv2.CAP_PROP_EXPOSURE))
cap.release()

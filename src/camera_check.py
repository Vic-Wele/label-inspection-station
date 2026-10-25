"""Find connected cameras and save one test frame from each."""
import cv2

for index in range(4):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Camera {index}: not found")
        continue
    ok, frame = cap.read()
    if ok:
        h, w = frame.shape[:2]
        path = f"data/raw/camera_test_{index}.jpg"
        cv2.imwrite(path, frame)
        print(f"Camera {index}: OK, {w}x{h}, saved {path}")
    else:
        print(f"Camera {index}: opened but no image")
    cap.release()

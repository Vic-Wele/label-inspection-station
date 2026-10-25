"""Open the webcam's driver settings panel with a live preview."""
import cv2

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_SETTINGS, 1)  # opens the settings panel

print("Press q in the preview window to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("Preview (press q to quit)", cv2.resize(frame, (960, 540)))
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

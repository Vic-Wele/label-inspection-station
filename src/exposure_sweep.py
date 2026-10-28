"""Try several exposures and report brightness, clipping and barcode reads for each."""
import cv2
import zxingcpp

from camera import open_camera

ROI = (380, 980, 650, 1450)  # label pocket: y0, y1, x0, x1

cap = open_camera(verbose=False)
print(f"{'exposure':>8} {'label brightness':>17} {'clipped %':>10} {'barcode':>10}")
for exp in [-4, -5, -6, -7, -8]:
    cap.set(cv2.CAP_PROP_EXPOSURE, exp)
    for _ in range(8):  # let the new exposure settle
        cap.read()
    ok, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[ROI[0]:ROI[1], ROI[2]:ROI[3]]
    big = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    reads = zxingcpp.read_barcodes(big)
    text = reads[0].text if reads else "NO READ"
    clipped = (roi >= 250).mean() * 100
    print(f"{exp:>8} {roi.mean():>17.1f} {clipped:>10.1f} {text:>10}")
    cv2.imwrite(f"data/raw/sweep_exp{exp}.jpg", frame)
cap.release()

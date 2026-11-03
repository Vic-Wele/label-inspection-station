"""Central settings for the label inspection station."""
from pathlib import Path

import cv2

# Camera (Logitech C615 on USB)
CAMERA_INDEX = 1
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

# Camera settings. Redo from scratch with the new ring light.
# Order matters: turn auto modes off before setting manual values.
# Old tuned values (history only, do not reuse) are commented out.
CAMERA_SETTINGS = [
    ("autofocus off", cv2.CAP_PROP_AUTOFOCUS, 0),
    ("auto exposure off", cv2.CAP_PROP_AUTO_EXPOSURE, 0.25),
    ("auto white balance off", cv2.CAP_PROP_AUTO_WB, 0),
    # ("focus", cv2.CAP_PROP_FOCUS, 68),
    # ("exposure", cv2.CAP_PROP_EXPOSURE, -7),
    # ("white balance", cv2.CAP_PROP_WB_TEMPERATURE, 6500),
    # ("brightness", cv2.CAP_PROP_BRIGHTNESS, 105),
    # ("contrast", cv2.CAP_PROP_CONTRAST, 58),
    # ("saturation", cv2.CAP_PROP_SATURATION, 0),
    # ("sharpness", cv2.CAP_PROP_SHARPNESS, 128),
    # ("gain", cv2.CAP_PROP_GAIN, 5),
    # ("backlight comp", cv2.CAP_PROP_BACKLIGHT, 1),
]

# Region of interest around the label pocket: (y0, y1, x0, x1).
# Not set yet. Find it in step 4i.
ROI = None

# Data (Google Drive backup)
DATA_DIR = Path("G:/My Drive/label-inspection-data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
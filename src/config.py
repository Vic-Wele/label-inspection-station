"""Central settings for the label inspection station."""
from pathlib import Path

# Camera
CAMERA_INDEX = 1          # USB Logitech webcam
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

# Data (Google Drive, synced to the cloud for Colab)
DATA_DIR = Path("G:/My Drive/label-inspection-data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

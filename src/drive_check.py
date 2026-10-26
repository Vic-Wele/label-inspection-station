"""Check that the station can write to the Google Drive data folder."""
from datetime import datetime
from config import RAW_DIR

test_file = RAW_DIR / "drive_test.txt"
test_file.write_text(f"Written from the station at {datetime.now()}\n")
print("Wrote:", test_file)
print("Exists:", test_file.exists())

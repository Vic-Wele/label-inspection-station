Camera Setup

Last updated: November 12, 2026

This document describes the current camera hardware, configuration, lighting requirements, calibration procedure, and test results used for image capture and inspection.

Hardware & Physical Setup
Component	Configuration
Camera	Logitech C615
Connection	USB through a hub
Camera Index	1
Resolution	1920 × 1080
Format	MJPG
Backend	DirectShow
Mount	Boom-arm tripod, pointing straight down
Lighting	Heyday LED bar on a separate tripod, positioned upper left
Image Scale	Approximately 9 px/mm
Station Requirements
Ceiling light must remain OFF during image capture and live inspection.
Heyday LED brightness must match the training images.
Camera and light positions should remain fixed after calibration.
Camera Configuration

The following settings are configured in src/config.py.

Setting	Value	Reason
Autofocus	Off	Prevents focus drift.
Focus	85	Sharpest setting at label height. The camera adjusts focus in steps of 17; a requested value of 90 rounds to 85.
Auto Exposure	Off	Prevents brightness changes between parts.
Exposure	-6	Brightest setting with 0% clipping and a safe margin.
Auto White Balance	Off	Maintains a fixed image response.
White Balance	4000	Fixed setting; color is irrelevant with saturation set to 0.
Brightness	128	Driver default.
Contrast	32	Driver default.
Saturation	0	Grayscale images; labels are black and white.
Sharpness	22	Driver default; produces clean edges without halos.
Gain	28	Driver default.
Backlight Compensation	0	Disabled to prevent automatic scene adjustments.

Additional driver setting (not configured in src/config.py):

Low Light Compensation: OFF
Applying Camera Settings

Run the following command to apply all camera settings and perform a self-check:

bash
python src/camera.py


The self-check passes after unplugging and reconnecting the camera.

Lighting & Brightness Calibration

Before each run, verify image brightness using the reference card.

Reference conditions:

Card 1 positioned in the dip.
Ceiling light OFF.
Camera and light in their calibrated positions.

Run the brightness check:

bash
python src/light_check.py

Expected Brightness
Measurement	Expected Value
Target brightness	94
Acceptable range	90–99

If brightness falls outside this range, adjust the Heyday LED brightness, not the camera settings.

Calibration Notes

The camera self-check cannot detect physical movement of the camera or light.

The brightness check detects changes in lighting.
The card locator compensates for small camera position shifts.

Both checks are important for maintaining consistent inspection results.

Image Processing

The inspection pipeline does not use a fixed image crop.

Instead, it:

Locates the inspection card.
Measures the card's tilt.
Corrects the image orientation.
Crops the image around the detected card.
Reads the barcode from the resulting crop without zooming.

Implementation: src/locate.py

This approach makes inspection more tolerant of small camera position changes.

Test Results
Exposure Sweep

The exposure sweep was performed during the initial setup under the following conditions:

Heyday LED at full brightness.
Room lights OFF.
Brightness, contrast, and gain held at their configured values.
Exposure	Label Brightness	Clipped Pixels	Barcode
-2	237.7	73.0%	No Read
-3	227.4	67.7%	Read
-4	211.9	55.0%	Read
-5	185.5	0.0%	Read
-6	139.9	0.0%	Read (Selected)
-7	96.1	0.0%	Read
-8	70.6	0.0%	Read
-9	50.2	0.0%	Read
-10	36.2	0.0%	Read
-11	28.4	0.0%	No Read

Selected exposure: -6

This setting provides sufficient image brightness with no clipped pixels and a safe margin against overexposure.

Additional Tests
Test	Result
Ceiling light ON	Brightness increased by 4.6% (within the 5% limit).
Barcode recognition	76/76 good images successfully read (100%).

Although the ceiling light test remained within the acceptable 5% variation, the station requirement remains ceiling light OFF during all captures and live runs.

Setup History & Lessons Learned
Previous Setup
Initially used a USB ring light.
Later switched to the Heyday LED at full brightness.
Image inspection originally relied on a fixed region of interest (ROI).
Camera & Lighting Shift

The camera was accidentally bumped, and the light was moved, resulting in a 26% increase in image brightness.

The following changes were made:

Dimmed the Heyday LED to restore the original brightness.
Replaced the fixed ROI approach with card detection and automatic cropping.
Improved tolerance to small camera position changes.
Lessons Learned
Mark camera and light positions using tape on the table or tripod.
Avoid changing camera settings after calibration.
Verify brightness before running inspections.
Keep lighting consistent with the training images.
Use card detection instead of relying on a fixed image region.

Important: Consistent camera positioning, fixed camera settings, and controlled lighting are essential for reliable image capture and barcode inspection.

# Camera Setup

*Current setup as of November 12, 2026.*

---

## Hardware

### Camera
- **Model:** Logitech C615
- **Connection:** USB (through a hub)
- **Camera Index:** 1
- **Resolution:** 1920 × 1080
- **Format:** MJPG
- **Backend:** DirectShow

### Mount
- Boom-arm tripod
- Pointing straight down

### Lighting
- Heyday LED bar on its own tripod
- Positioned upper-left of the station
- Dimmed to match the training images

### Station Rules
- Keep the **ceiling light OFF** during captures and live runs

### Scale
- Approximately **9 px/mm**

---

## Locked Camera Settings (`src/config.py`)

| Setting | Value | Reason |
|----------|---------|---------|
| Autofocus | Off | Autofocus drifts |
| Focus | 85 | Sharpest at label height. Camera moves focus in steps of 17, so 90 rounds to 85 |
| Auto Exposure | Off | Prevents brightness changes between parts |
| Exposure | -6 | Brightest setting with 0% clipping and a safe margin |
| Auto White Balance | Off | Fixed response |
| White Balance | 4000 | Color doesn't matter with saturation set to 0 |
| Brightness | 128 | Driver default; sweep performed at this value |
| Contrast | 32 | Driver default; sweep performed at this value |
| Saturation | 0 | Grayscale; labels are black and white |
| Sharpness | 22 | Driver default; clean edges without halos |
| Gain | 28 | Driver default; sweep performed at this value |
| Backlight Compensation | 0 | Counts as an automatic adjustment |

### Driver Settings (Not Controlled by `config.py`)

| Setting | Value |
|----------|---------|
| Low Light Compensation | OFF |

---

## Startup Validation

Run:

```bash
python src/camera.py
```

This:

- Applies all configured camera settings
- Performs a camera self-check

Expected result:

✅ Self-check passes, even after unplugging and reconnecting the camera.

---

## Brightness Reference

Before every run:

1. Place **Card 1** in the dip.
2. Verify the ceiling light is **OFF**.
3. Run:

```bash
python src/light_check.py
```

### Expected Brightness

Whole-image brightness should be approximately:

```text
94
```

Acceptable range:

```text
90 - 99
```

If brightness is outside this range:

✅ Adjust the **Heyday light**

❌ Do NOT adjust camera settings

### Why This Check Exists

The camera self-check cannot detect:

- A moved camera
- A moved light

The brightness check verifies lighting consistency, while the card locator compensates for small camera shifts.

---

## Image Processing Workflow

Inspection does **not** use a fixed crop.

The system:

1. Locates the card
2. Measures card tilt
3. Straightens the image
4. Crops around the card
5. Reads the barcode from the corrected crop

Implementation:

```text
src/locate.py
```

No barcode zoom is used.

---

## Test Results

### Exposure Sweep

Conditions:

- Initial setup
- Heyday light at full brightness
- Room lights off

| Exposure | Label Brightness | Clipped % | Barcode Result |
|-----------|-----------------|-----------|----------------|
| -2 | 237.7 | 73.0 | ❌ No Read |
| -3 | 227.4 | 67.7 | ✅ Read |
| -4 | 211.9 | 55.0 | ✅ Read |
| -5 | 185.5 | 0.0 | ✅ Read |
| **-6** | **139.9** | **0.0** | ✅ **Selected** |
| -7 | 96.1 | 0.0 | ✅ Read |
| -8 | 70.6 | 0.0 | ✅ Read |
| -9 | 50.2 | 0.0 | ✅ Read |
| -10 | 36.2 | 0.0 | ✅ Read |
| -11 | 28.4 | 0.0 | ❌ No Read |

### Room Light Test

Turning the ceiling light on changed brightness by:

```text
4.6%
```

This is below the 5% limit.

Operational rule remains:

> Keep the ceiling light OFF during capture and live operation.

### Barcode Validation

- Barcode read without zoom: **76 / 76**
- Success rate: **100%**

---

## Change History

### Original Setup

- USB ring light
- Fixed ROI (Region of Interest)

### Issue Encountered

At one point:

- Camera position changed
- Light position changed
- Brightness increased by approximately **26%**

### Fix Implemented

- Dimmed the Heyday light to match the original setup
- Replaced fixed ROI processing with card localization and alignment

### Lesson Learned

Mark both the camera and light locations with tape or physical alignment marks.

This allows the station to be restored quickly after accidental movement.

---

## Operational Checklist

Before running inspection:

- [ ] Camera in marked position
- [ ] Light in marked position
- [ ] Ceiling light OFF
- [ ] Card 1 in the dip
- [ ] `python src/light_check.py` reports brightness between 90 and 99
- [ ] `python src/camera.py` self-check passes

When all checks pass, the station is ready for operation.

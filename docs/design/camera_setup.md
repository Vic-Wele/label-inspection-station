# Camera Setup

Redone from scratch in November 2026 after switching to the Heyday LED bar light.

## Hardware

- Camera: Logitech C615, USB, index 1, 1920 x 1080, MJPG, DirectShow backend
- Mount: boom-arm tripod, pointing straight down (top and bottom label edges within about 1% in width)
- Light: Heyday LED bar on its own tripod, upper left, full brightness
- Station rule: ceiling light OFF during capture and live runs
- Scale: about 9.2 px per mm (label about 1015 px wide)

## Locked settings (src/config.py)

| Setting | Value | Why |
|---|---|---|
| Autofocus | Off | Autofocus drifts |
| Focus | 85 | Sharpest at label height (camera moves in steps of 17; 90 rounds to 85) |
| Auto exposure | Off | Auto changes brightness from part to part |
| Exposure | -6 | Brightest setting with 0% clipping and a safe margin (see sweep) |
| Auto white balance | Off | Fixed response |
| White balance | 4000 | Fixed; color doesn't matter with saturation 0 |
| Brightness | 128 | Driver default; sweep done at this value |
| Contrast | 32 | Driver default; sweep done at this value |
| Saturation | 0 | Grayscale; labels are black and white |
| Sharpness | 22 | Driver default; clean edges, no halos |
| Gain | 28 | Driver default; sweep done at this value |
| Backlight compensation | 0 | Adjusts to the scene, so it counts as an auto setting |

Driver panel only (not in config.py): Low Light Compensation OFF. Checked after a power cycle by brightness: 138.1 vs 137.8 before.

Changing brightness, contrast or gain changes the image brightness. If any of them change, redo the exposure sweep.

## Region of interest

ROI = (60, 1040, 330, 1460) as (y0, y1, x0, x1).

- Set after focus, because changing focus changes the zoom slightly.
- Card position over 7 re-seats: box x 384 to 1437, y 111 to 992. Always inside the ROI.
- Hands-off drift test: under 1 px over 3 minutes. Nothing creeps on its own.
- Check tool: python src/card_position.py

## Test results

Exposure sweep (Heyday full, room lights off):

| Exposure | Label brightness | Clipped % | Barcode |
|---|---|---|---|
| -2 | 237.7 | 73.0 | NO READ |
| -3 | 227.4 | 67.7 | Read |
| -4 | 211.9 | 55.0 | Read |
| -5 | 185.5 | 0.0 | Read |
| -6 | 139.9 | 0.0 | Read (chosen) |
| -7 | 96.1 | 0.0 | Read |
| -8 | 70.6 | 0.0 | Read |
| -9 | 50.2 | 0.0 | Read |
| -10 | 36.2 | 0.0 | Read |
| -11 | 28.4 | 0.0 | NO READ |

- Room light test: lights off 138.1, ceiling light on 144.4 (+4.6%, under the 5% limit)
- Power-cycle test (unplug, replug): self-check PASS, all 9 settings
- Barcode read (ROI + 2x zoom): 10/10, average 101 ms

## Previous setup (history only, do not reuse)

Ring light, focus 68, exposure -7, white balance 6500, brightness 105, contrast 58, gain 5, sharpness 128, saturation 0, backlight 1, ROI (380, 980, 650, 1450), about 5.6 px per mm. Replaced when the light changed.
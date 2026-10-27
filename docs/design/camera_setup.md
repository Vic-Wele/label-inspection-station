# Station Camera and Lighting Setup

## Geometry

| Item | Value |
| --- | --- |
| Camera | Logitech C615 USB webcam, 1920 x 1080 |
| Mounting | Overhead boom arm, lens pointing straight down |
| Field of view | Whole box top plus a thin black border |
| Resolution on the part | About 5.6 pixels per mm |
| Barcode bar width | About 2.3 pixels per bar (reads reliably, about 55-70 ms) |
| Part handling | Box in a two-wall nest; label card in a four-sided pocket |

## Lighting

| Choice | Reason |
| --- | --- |
| Ring light, camera looking through the center | Even light from all sides, few shadows |
| Ring light at full brightness | Brighter scene allows a short exposure, so images stay sharp |
| Room lights off or blocked | The station's own light is the only light, so images don't change with the time of day |

## Locked camera settings

| Setting | Value | Reason |
| --- | --- | --- |
| Focus | 68 (manual) | Sharpest at the label height; autofocus can drift between parts |
| Exposure | -5 (manual) | Bright enough with the ring light; auto exposure changes when a white label enters the view |
| White balance | 6500 (manual) | Fixed color response |
| Saturation | 0 | Grayscale image; labels are black and white, and many industrial cameras are monochrome |
| Sharpness | 128 (default) | Higher values add white halos around text, which are camera effects, not real label features |
| Brightness / contrast / gain | 105 / 58 / 5 | Tuned for clear black-on-white contrast |
| Low light compensation | Off | An automatic feature that can change brightness without warning |

## Startup self-check

Every time the station opens the camera, `src/camera.py` applies all settings, reads them back, and prints PASS or FAIL. The station should not inspect parts after a FAIL.

## Lessons learned

- Auto settings looked better in a quick preview, but they change from part to part. Locking everything gives repeatable images.
- The camera's own preview hid a problem: Low Light Compensation was brightening the image. Turning it off showed the true locked image.
- More light is better than longer exposure: it keeps images sharp.

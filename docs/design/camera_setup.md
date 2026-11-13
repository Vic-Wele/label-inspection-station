# \# Camera Setup

# 

# Current setup as of November 12, 2026.

# 

# \## Hardware

# 

# \- Camera: Logitech C615, USB (through a hub), index 1, 1920 x 1080, MJPG, DirectShow backend

# \- Mount: boom-arm tripod, pointing straight down

# \- Light: Heyday LED bar on its own tripod, upper left, dimmed to match the training images

# \- Station rule: ceiling light OFF during capture and live runs

# \- Scale: about 9 px per mm

# 

# \## Locked settings (src/config.py)

# 

# | Setting | Value | Why |

# |---|---|---|

# | Autofocus | Off | Autofocus drifts |

# | Focus | 85 | Sharpest at label height (camera moves focus in steps of 17; 90 rounds to 85) |

# | Auto exposure | Off | Auto changes brightness from part to part |

# | Exposure | -6 | Brightest setting with 0% clipping and a safe margin (sweep below) |

# | Auto white balance | Off | Fixed response |

# | White balance | 4000 | Fixed; color doesn't matter with saturation 0 |

# | Brightness | 128 | Driver default; sweep done at this value |

# | Contrast | 32 | Driver default; sweep done at this value |

# | Saturation | 0 | Grayscale; labels are black and white |

# | Sharpness | 22 | Driver default; clean edges, no halos |

# | Gain | 28 | Driver default; sweep done at this value |

# | Backlight compensation | 0 | Adjusts to the scene, so it counts as an auto setting |

# 

# Driver panel only (not in config.py): Low Light Compensation OFF.

# 

# `python src/camera.py` applies all settings and runs a self-check. It passes after an unplug and replug.

# 

# \## Brightness reference

# 

# Before any run, with card 1 in the dip and the ceiling light off:

# 

# &#x20;   python src/light\_check.py

# 

# Whole image brightness should be about \*\*94\*\* (accept 90 to 99). If not, adjust the Heyday's brightness, not the camera.

# 

# The self-check can't detect a moved camera or a moved light. This brightness check covers the light; the card locator covers small camera shifts.

# 

# \## How the image is used

# 

# The inspection doesn't use a fixed crop. It locates the card, measures its tilt, straightens it and crops around it (`src/locate.py`). The barcode is read on that crop with no zoom.

# 

# \## Test results

# 

# Exposure sweep (first setup, Heyday at full, room lights off):

# 

# | Exposure | Label brightness | Clipped % | Barcode |

# |---|---|---|---|

# | -2 | 237.7 | 73.0 | NO READ |

# | -3 | 227.4 | 67.7 | Read |

# | -4 | 211.9 | 55.0 | Read |

# | -5 | 185.5 | 0.0 | Read |

# | -6 | 139.9 | 0.0 | Read (chosen) |

# | -7 | 96.1 | 0.0 | Read |

# | -8 | 70.6 | 0.0 | Read |

# | -9 | 50.2 | 0.0 | Read |

# | -10 | 36.2 | 0.0 | Read |

# | -11 | 28.4 | 0.0 | NO READ |

# 

# \- Room light test: ceiling light on changed brightness by 4.6% (under the 5% limit). Rule: ceiling light off anyway.

# \- Barcode read without zoom: 76/76 good images.

# 

# \## History

# 

# \- First setup used a USB ring light, then the Heyday at full brightness with a fixed ROI.

# \- The camera was later bumped and the light moved (26% brighter). Fix: the light was dimmed to match, and the inspection switched to locating the card instead of a fixed ROI.

# \- Lesson: mark the positions of the camera and the light (tape on the table or tripod) so they can be restored.


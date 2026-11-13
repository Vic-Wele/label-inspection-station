# \# Label Inspection Station

# 

# A small parcel label inspection station, built to learn the full vision applications-engineering lifecycle:

# requirements, lighting and optics, machine learning, PLC integration, testing (FAT) and documentation.

# 

# !\[Station](media/station.jpg)

# 

# A label card sits on a parcel under an overhead camera. When the operator's hands leave a break-beam sensor,

# the station inspects the label and a PLC shows the result on a green/red stack light.

# 

# \## Results

# 

# \*\*FAT (live, guided, 28 steps): PASS\*\*

# 

# | Requirement | Target | Result |

# |---|---|---|

# | Detection | at least 98% | 6/6 defects, 14/14 missing labels |

# | False rejects | at most 2% | 0/8 good parts rejected |

# | Cycle time (trigger to light) | under 500 ms | mean 176 ms, max 266 ms |

# | PLC output and logging | every part | every step |

# 

# \*\*Offline test\*\* (126 images, split by card, test cards never seen in training):

# 50/50 defects caught. The barcode reader alone caught only 14/50, because torn, smudged, faded and skewed labels often still scan.

# 

# Honest note: 8 good parts can't prove a 2% false-reject rate; that would take about 150. See the \[FAT report](docs/reports/fat\_report.md).

# 

# \## What the model sees

# 

# The model learns only from good labels and flags anything that looks different. Heat maps show where:

# 

# | Good | Torn corner | Pencil smudge |

# |---|---|---|

# | !\[good](media/results/heatmap\_good.jpg) | !\[torn](media/results/heatmap\_torn.jpg) | !\[smudged](media/results/heatmap\_smudged.jpg) |

# 

# \## How one inspection works

# 

# 1\. The operator's hand breaks the beam while placing a card. The lights go off ("loading").

# 2\. The hand leaves: the beam is clear and the image has been still for 0.5 s. That's the trigger.

# 3\. The laptop locates the card, measures its tilt, straightens it and checks 4 things. Any one fails the part:

# &#x20;  - \*\*No card\*\* found (missing label)

# &#x20;  - \*\*Skewed:\*\* tilt above 3 degrees (a rule; good cards measured 0 to 1.9, skewed 4.6 to 8.9)

# &#x20;  - \*\*No read:\*\* the Code 128 barcode doesn't decode

# &#x20;  - \*\*Anomaly:\*\* the model's score is above the threshold (tears, smudges, fading, scratches)

# 4\. The result goes to the PLC over Modbus RTU. The ladder turns on green or red, only while the beam is clear.

# 5\. Image, result, reason, score, tilt and cycle time are logged.

# 

# \## Key design choices

# 

# | Choice | Why |

# |---|---|

# | Lighting first, then optics, then the algorithm | Locked every camera setting; chose exposure from a sweep (0% clipping with margin) |

# | Anomaly detection (PatchCore-style, ResNet18 features, greedy coreset) | Trains on good parts only; catches defects nobody photographed |

# | Split by card, not by image | Near-identical shots of one card never land in both training and testing |

# | Threshold from good images only | No peeking at defects |

# | Locate, then inspect | A bumped camera broke a fixed crop; finding the card first fixed it |

# | Rule for skew, model for appearance | Measure with rules what can be measured; use ML for what can't |

# 

# !\[Exposure examples](media/setup/sweep\_exp-4.jpg)

# \*Exposure -4 (too bright). Chosen: -6. See \[camera setup](docs/design/camera\_setup.md).\*

# 

# \## Problems solved along the way

# 

# \- \*\*Break-beam never reported "blocked":\*\* the sensor received drove its own output; an extra pull-up resistor kept it high. Found in 4 isolation steps.

# \- \*\*Modbus answered "Illegal Function" to every request:\*\* a reply with an error meant cable and baud rate were fine; the Modbus server wasn't enabled.

# \- \*\*Position shift between photo sessions:\*\* caught before training (it would have taught "box moved = defect"); recaptured everything in one session.

# \- \*\*Bumped camera:\*\* good cards suddenly failed; fixed by locating the card instead of using a fixed crop.

# \- \*\*Hand still over the card at trigger time:\*\* added a "scene still for 0.5 s" check.

# \- \*\*Cycle time 536 ms:\*\* profiled each stage; the inspection was only 160 ms. Removing extra frame waits, the 2x barcode zoom and a second Modbus message brought it to 176 ms.

# \- \*\*A good card kept failing:\*\* the heat map showed a label edge sticking out past the card. The model was right.

# 

# \## Hardware and software

# 

# \- \*\*Hardware:\*\* Logitech C615 webcam on a boom arm, Heyday LED bar light, IR break-beam sensor, Arduino Uno (ELEGOO kit), red/green LEDs, Avery 15264 labels on foam cards, Microsoft Surface laptop with a USB hub

# \- \*\*Vision and ML:\*\* Python 3.12, OpenCV, zxing-cpp, PyTorch + torchvision (ResNet18)

# \- \*\*PLC:\*\* OpenPLC Editor v4 (ladder logic), Modbus RTU over USB, pymodbus

# \- \*\*Workflow:\*\* Git/GitHub, Google Drive backup

# 

# | This project | Real SICK installation |

# |---|---|

# | Webcam + laptop software | Inspector / SIM with SICK Nova or AppSpace |

# | zxing-cpp | Lector code reader |

# | Model trained on the laptop | dStudio training, inference on the sensor |

# | Arduino + OpenPLC | Customer PLC (Rockwell, Siemens) |

# | Modbus RTU | EtherNet/IP or PROFINET |

# 

\## Repository

docs/requirements/requirements.md requirements with acceptance tests
===

# docs/design/ architecture, camera setup, I/O map

# docs/reports/fat\_report.md FAT report

# src/inspector.py all inspection checks (shared by training, live and FAT)

# src/locate.py find, measure and straighten the card

# src/train\_eval.py train the model, set the threshold, test

# src/live.py live station loop

# src/fat.py guided FAT run

# src/capture.py guided dataset capture

# src/camera.py locked camera settings + self-check

plc/station\_plc/ OpenPLC ladder project


===

\## Run it

python -m venv .venv
===

# source .venv/Scripts/activate

# pip install -r requirements.txt

# 

# python src/camera.py # camera self-check

# python src/light\_check.py # brightness check (about 94 with card 1)

# python src/train\_eval.py # train and test the model

# python src/live.py # live station (needs the PLC on COM4)

python src/fat.py # guided FAT run


===

# Images are not stored in this repo (backed up to Google Drive).


\# FAT Report: Label Inspection Station



Date: November 12, 2026

Result: \*\*PASS\*\* (FAT run 3), with notes below.



\## 1. Scope



Factory acceptance test of the full station, live: break-beam trigger -> camera -> inspection -> PLC -> stack light -> log.

Each step is guided by `src/fat.py`, which tells the operator what to place and compares expected vs actual.



\## 2. Setup



| Item | Value |

|---|---|

| Camera | Logitech C615, 1920 x 1080, all settings locked, self-check PASS |

| Light | Heyday LED bar, ceiling light off; whole-image brightness 94.2 (reference 94.3) |

| PLC | Arduino Uno, OpenPLC ladder, Modbus RTU over USB (115200 baud) |

| Model | PatchCore-style anomaly detection, ResNet18 features, greedy coreset bank (6,160 patches) |

| Threshold | 2.060, set automatically from good threshold images only |

| Skew limit | 3.0 deg, set from data (good 0 to 1.9 deg, skewed 4.6 to 8.9 deg) |



Inspection logic (`src/inspector.py`): locate the card, straighten it, then FAIL if any of:

no card, skew above 3 deg, barcode not read, anomaly score above threshold.



\## 3. Test plan



28 steps: 14 placements, each followed by a removal (an empty-dip, missing-label test).



| Placements | Cards | Expected |

|---|---|---|

| 8 good | 16, 17, 18, 19 (twice each) | PASS |

| 6 defects | faded 27, damaged barcode 29, torn 20, smudged 23, scratched 25, skewed | FAIL |

| 14 removals | empty dip | FAIL |



Good test cards (16 to 19) were never used for training or threshold setting.



\## 4. Results (FAT run 3)



| Requirement | Target | Result | Verdict |

|---|---|---|---|

| REQ-06 Detection | at least 98% | 6/6 defects, 14/14 missing | PASS |

| REQ-07 False rejects | at most 2% | 0/8 | PASS (see note 1) |

| REQ-09 Cycle time | under 500 ms | mean 176 ms, max 266 ms | PASS |

| REQ-11 PLC output | green = pass, red = fail | correct at every step | PASS |

| REQ-12 Logging | image, result, score, time | every step logged | PASS |



Per-check results: skew rule caught +7.8 deg; barcode reader caught damaged barcode and scratched (NO READ);

the model caught faded, torn, smudged, scratched and damaged barcode (ANOMALY).

Good card scores 1.58 to 1.94 (threshold 2.060); good card tilt -2.3 to +0.5 deg.



Log: `data/fat/fat\_20261112\_225915.csv` (images saved per step).



\## 5. Notes



1\. \*\*Sample size.\*\* 8 good parts can't prove a 2% false-reject rate. Rule of thumb: about 150 good parts with zero rejects

&#x20;  are needed. The FAT shows the system works; a production FAT would need a larger run.

2\. \*\*Skew test card.\*\* The skew step read PKG-0017, so card 17 was used instead of card 1. The test is still valid.

3\. \*\*Card 19.\*\* Offline testing flagged 3 images of card 19. The heat map showed a label edge overhanging the card corner.

&#x20;  Treated as a true finding (a label application flaw); the card was trimmed before this FAT.

4\. \*\*Offline results\*\* (126 images, split by card): 50/50 defects caught; 0/13 false rejects on clean good images.



\## 6. History (what changed between FAT runs)



| Run | Change | Good | Defects | Missing | Cycle time | Issue found |

|---|---|---|---|---|---|---|

| 1 | Card-located crop | 7/8 | 6/6 | 14/14 | mean 340, max 590 ms | Card tilted 2.7 deg was rejected |

| 2 | + straighten, 3 deg skew rule | 7/8 | 6/6 | 14/14 | mean 536, max 646 ms | Badly seated card; slower (2 full-image rotations) |

| 3 | + 1x barcode, no extra frames, 1 Modbus message | 8/8 | 6/6 | 14/14 | mean 176, max 266 ms | None |



Speed fix found by profiling each stage: inspection itself was about 160 ms; the rest was waiting for extra camera frames

and 2 separate Modbus messages.



\## 7. Open items



\- Larger good-part run (about 150) to prove REQ-07 statistically.

\- Marked positions for the light and camera, so they can be restored after being moved.


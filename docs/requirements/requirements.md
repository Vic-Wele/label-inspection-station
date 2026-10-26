# Label Inspection Station: Requirements

## 1. Purpose

Automatically inspect shipping labels on parcels, flag defective parcels, and log every result.

## 2. Scope

**Included**
- One camera inspection station with controlled lighting
- Defect detection with rule-based checks and an AI model
- Barcode reading (Code 128)
- Pass/fail signal to a PLC, which drives a reject flag and a red/green stack light
- Logging and a live dashboard

**Excluded**
- A motorized conveyor (parcels are placed by hand into a fixed nest)
- A physical diverter that pushes parcels off the line (rejection is signaled at the station)
- Integration with a real warehouse or sorting system
- Safety-rated guarding (not needed for this low-power demo)

## 3. Product

- Shipping box, about 24 x 15 x 9.5 cm
- Shipping label, 3 1/3 x 4 inches (Avery 15264), printed black-and-white on a laser printer
- Label content: product name, Code 128 barcode, lot code
- Each label is mounted on a thin card and placed in a corner guide on the top face of the box, so labels can be swapped quickly

## 4. Requirements

| ID | Requirement | Target | How it will be tested |
| --- | --- | --- | --- |
| REQ-01 | Detect missing labels | Included in REQ-06 | FAT with no label card |
| REQ-02 | Detect skewed labels | Included in REQ-06 | FAT with label cards placed crooked |
| REQ-03 | Detect torn labels | Included in REQ-06 | FAT with torn label cards |
| REQ-04 | Detect smudged or faded print | Included in REQ-06 | FAT with faded and smudged label cards |
| REQ-05 | Detect unreadable barcodes | Included in REQ-06 | FAT with damaged-barcode label cards |
| REQ-06 | Detection rate | At least 98% of defective parcels flagged | FAT: count flagged defective parcels |
| REQ-07 | False reject rate | At most 2% of good parcels flagged | FAT: count flagged good parcels |
| REQ-08 | Barcode read rate | At least 99% on good labels | FAT: count successful reads |
| REQ-09 | Cycle time | Result in under 500 ms after the trigger | Log timestamps for every parcel |
| REQ-10 | Station readiness | Ready for the next parcel within 2 seconds of the previous trigger | Log timestamps for every parcel |
| REQ-11 | PLC output | On fail: reject flag raised and red light on. On pass: green light on. | Check flag and lights on every parcel |
| REQ-12 | Logging | Every inspection saved with image, result, confidence and time | Check log matches the FAT count |

## 5. Assumptions

- Room light is blocked or controlled by the station's own light.
- The camera and light do not move after setup.
- All label cards are cut to the same size.
- The station is kept out of direct sunlight (it can interfere with the IR sensor).

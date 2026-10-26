# Label Inspection Station: Requirements

## 1. Purpose

Automatically inspect printed labels on small boxes, reject defective boxes, and log every result.

## 2. Scope

**Included**
- One camera inspection station with controlled lighting
- Defect detection with rule-based checks and an AI model
- Barcode reading (Code 128)
- Pass/fail signal to a PLC, which fires a reject arm
- Logging and a live dashboard

**Excluded**
- A motorized conveyor (boxes are moved by hand or slide down a chute)
- Integration with a real factory MES or ERP system
- Safety-rated guarding (not needed for this low-power demo)

## 3. Product

- Small kraft box, about 2 x 2 inches
- Printed label: product name, Code 128 barcode, lot code

## 4. Requirements

| ID | Requirement | Target | How it will be tested |
| --- | --- | --- | --- |
| REQ-01 | Detect missing labels | Included in REQ-06 | FAT with missing-label boxes |
| REQ-02 | Detect skewed labels | Included in REQ-06 | FAT with skewed-label boxes |
| REQ-03 | Detect torn labels | Included in REQ-06 | FAT with torn-label boxes |
| REQ-04 | Detect smudged or faded print | Included in REQ-06 | FAT with smudged-print boxes |
| REQ-05 | Detect unreadable barcodes | Included in REQ-06 | FAT with damaged-barcode boxes |
| REQ-06 | Detection rate | At least 98% of defective boxes rejected | FAT: count rejected defective boxes |
| REQ-07 | False reject rate | At most 2% of good boxes rejected | FAT: count rejected good boxes |
| REQ-08 | Barcode read rate | At least 99% on good labels | FAT: count successful reads |
| REQ-09 | Cycle time | Result in under 500 ms after the trigger | Log timestamps for every part |
| REQ-10 | Throughput | Up to 30 boxes per minute | Timed FAT run |
| REQ-11 | PLC output | Pass/fail sent to the PLC; reject arm fires on fail | Check reject arm on every fail |
| REQ-12 | Logging | Every inspection saved with image, result, confidence and time | Check log matches the FAT count |

## 5. Assumptions

- Room lighting is blocked or controlled by the station's own light.
- The camera and light do not move after setup.
- All boxes come from the same batch.

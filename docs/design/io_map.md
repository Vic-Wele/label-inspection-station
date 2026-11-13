# PLC I/O Map and Wiring

---

## PLC Configuration

### Platform

- **PLC Runtime:** OpenPLC
- **Controller:** Arduino Uno
- **Communication:** Modbus RTU over USB Serial

---

## PLC I/O Mapping

| Arduino Pin | Type | PLC Address | Modbus Address | Alias | Variable | Description |
|-------------|------|-------------|----------------|--------|----------|-------------|
| 2 | Digital Input | `%IX0.0` | Discrete Input 0 (read) | `BEAM_SENSOR` | `beam_clear` | `TRUE` = beam clear, `FALSE` = hand in beam |
| 13 | Digital Output | `%QX0.0` | Coil 0 | `LED_TEST` | `fail_flag` | FAIL result from laptop (shown on onboard LED) |
| 7 | Digital Output | `%QX0.1` | Coil 1 | `GREEN_LIGHT` | `green_out` | Green stack light output |
| 8 | Digital Output | `%QX0.2` | Coil 2 | `RED_LIGHT` | `red_out` | Red stack light output |
| 12 | Digital Output | `%QX0.3` | Coil 3 | - | `pass_flag` | PASS result from laptop (not wired externally) |

### Arduino Uno OpenPLC Layout

The standard OpenPLC mapping for an Arduino Uno is:

#### Inputs

| Pins |
|------|
| 2, 3, 4, 5, 6 |

#### Outputs

| Pins |
|------|
| 7, 8, 12, 13 |

> **Important:** Pin 12 is configured as an output and cannot be used as an input.

---

## Ladder Logic

### Current Logic

| Rung | Logic |
|--------|--------|
| 1 | `beam_clear AND pass_flag → green_out` |
| 2 | `beam_clear AND fail_flag → red_out` |

### Behavior

- When the beam is clear and the inspection passes, the green light turns on.
- When the beam is clear and the inspection fails, the red light turns on.
- While the operator is loading a part and blocking the beam, both lights remain off.

---

## Communication (Laptop ↔ PLC)

| Setting | Value |
|----------|---------|
| Protocol | Modbus RTU over USB Serial |
| PLC Role | Slave (Server) |
| Laptop Role | Master (Client) |
| Port | COM4 |
| Baud Rate | 115200 |
| Serial Format | 8N1 |
| Slave ID | 1 |
| OpenPLC Requirement | Modbus Server must be added and enabled |

### OpenPLC Requirement

The Modbus Server must be **enabled** in OpenPLC.

Without it, every request returns:

```text
Exception 1 - Illegal Function
```

### Reads

The laptop continuously polls:

| Function | Address | Signal |
|-----------|---------|---------|
| Function 2 | Discrete Input 0 | `beam_clear` |

### Writes

The laptop writes all output coils in a single packet using Function 15:

```python
[fail_flag, False, False, pass_flag]
```

Corresponding coil assignments:

| Coil | Purpose |
|--------|---------|
| 0 | `fail_flag` |
| 1 | Green output (overridden by ladder logic) |
| 2 | Red output (overridden by ladder logic) |
| 3 | `pass_flag` |

### Important Note

Coils 1 and 2 are rewritten by the PLC ladder logic on every scan (approximately every 20 ms).

As a result, the laptop's values for those coils have no effect.

---

## Breadboard Wiring

### Power Distribution

| Signal | From | To |
|----------|------|------|
| 5V Supply | Arduino 5V | Breadboard positive rail, row 27 |
| Ground | Arduino GND (next to pin 13) | Breadboard negative rail, row 15 |

### Indicator Lights

| Device | From | To |
|----------|------|------|
| Green Light | Pin 7 | Row 10a → 220 Ω resistor (10c–14c) → Green LED (long leg 14a, short leg to GND rail) |
| Red Light | Pin 8 | Row 20a → 220 Ω resistor (20c–24c) → Red LED (long leg 24a, short leg to GND rail) |

### Break-Beam Sensor

| Connection | Wire Color | Destination |
|-------------|------------|------------|
| Emitter Power | Red / Black | Positive rail / Negative rail (row 29) |
| Receiver Power | Red / Black | Positive rail / Negative rail (row 25) |
| Receiver Signal | White | Row 28a |
| PLC Input | Pin 2 | Row 28d |

---

## Commissioning Notes

### Sensor Behavior

The received break-beam sensor differed from the originally designed model.

Because the sensor actively drives its output:

- No external pull-up resistor is required.
- A 10 kΩ pull-up resistor prevented the signal from going low.
- The pull-up resistor was removed.

### Fault Isolation Procedure

The following troubleshooting sequence was used:

1. Verify the emitter using a phone camera (infrared is visible).
2. Verify the PLC input by forcing row 28 to ground.
3. Remove the pull-up resistor after confirming the sensor's output behavior.

### Modbus Troubleshooting

Initially, every Modbus request returned:

```text
Illegal Function
```

This indicated that:

- USB communication was working.
- The baud rate was correct.
- The slave ID was correct.

The actual problem was:

- The Modbus Server was not enabled in OpenPLC.

Once enabled, communication worked normally.

### Program Deployment

After any ladder logic or PLC program modification:

1. Build the OpenPLC project.
2. Upload the updated program to the Arduino.

Changes do not take effect until the upload is completed.

### USB Connections

The laptop has only one USB port.

A USB hub is used to connect:

- The inspection camera
- The Arduino PLC

simultaneously.

---

## Operational Summary

### Inputs

| Signal | Source |
|----------|---------|
| `beam_clear` | Break-beam sensor |

### Outputs

| Signal | Device |
|----------|---------|
| `green_out` | Green stack light |
| `red_out` | Red stack light |
| `pass_flag` | Internal PLC flag |
| `fail_flag` | Internal PLC flag / onboard LED |

### Operator Behavior

| Beam State | Inspection Result | Light Output |
|------------|------------------|--------------|
| Blocked | Pass | Off |
| Blocked | Fail | Off |
| Clear | Pass | Green |
| Clear | Fail | Red |

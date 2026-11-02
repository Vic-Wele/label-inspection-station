# PLC I/O Map and Wiring

## PLC I/O (OpenPLC on Arduino Uno)

| Arduino pin | Type | PLC address | Alias | Variable | Meaning |
| --- | --- | --- | --- | --- | --- |
| 2 | Digital input | %IX0.0 | BEAM_SENSOR | beam_clear | TRUE = beam clear, FALSE = parcel present |
| 7 | Digital output | %QX0.1 | GREEN_LIGHT | green_out | Green stack light |
| 8 | Digital output | %QX0.2 | RED_LIGHT | red_out | Red stack light (reject) |
| 13 | Digital output | %QX0.0 | LED_TEST | led_out | On-board test light |

Note: in OpenPLC's standard Uno layout, digital inputs are pins 2 to 6 and digital outputs are pins 7, 8, 12 and 13. Pin 12 cannot be used as an input.

## Breadboard wiring

| Item | From | To |
| --- | --- | --- |
| 5V supply | Arduino 5V | + rail, row 27 |
| Ground | Arduino GND (next to pin 13) | - rail, row 15 |
| Green light | Pin 7 | Row 10a, 220 ohm (10c to 14c), green LED (long leg 14a, short leg - rail) |
| Red light | Pin 8 | Row 20a, 220 ohm (20c to 24c), red LED (long leg 24a, short leg - rail) |
| Emitter | Red / black | + rail / - rail, row 29 |
| Receiver power | Red / black | + rail / - rail, row 25 |
| Receiver signal | White | Row 28a |
| PLC input | Pin 2 | Row 28d |

## Ladder logic (current)

| Rung | Logic |
| --- | --- |
| 1 | Always on: led_out |
| 2 | beam_clear (normally open) to green_out |
| 3 | beam_clear (normally closed) to red_out |

## Commissioning notes

- The break-beam sensor received was a different model than designed for. It drives its own output, so no external pull-up is used. An extra 10 kOhm pull-up prevented the signal from going low.
- Fault isolation steps used: emitter checked with a phone camera (infrared visible), PLC input checked by forcing row 28 to ground, then the pull-up was removed.
- After any program change, the program must be built and uploaded to the Arduino.

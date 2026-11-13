# \# PLC I/O Map and Wiring

# 

# \## PLC I/O (OpenPLC on Arduino Uno)

# 

# | Arduino pin | Type | PLC address | Modbus | Alias | Variable | Meaning |

# | --- | --- | --- | --- | --- | --- | --- |

# | 2 | Digital input | %IX0.0 | Discrete input 0 (read) | BEAM\_SENSOR | beam\_clear | TRUE = beam clear, FALSE = hand in beam |

# | 13 | Digital output | %QX0.0 | Coil 0 (written by laptop) | LED\_TEST | fail\_flag | Laptop result: FAIL (on-board amber LED shows it) |

# | 7 | Digital output | %QX0.1 | Coil 1 | GREEN\_LIGHT | green\_out | Green stack light |

# | 8 | Digital output | %QX0.2 | Coil 2 | RED\_LIGHT | red\_out | Red stack light |

# | 12 | Digital output | %QX0.3 | Coil 3 (written by laptop) | - | pass\_flag | Laptop result: PASS (nothing wired to pin 12) |

# 

# Note: in OpenPLC's standard Uno layout, digital inputs are pins 2 to 6 and digital outputs are pins 7, 8, 12 and 13. Pin 12 cannot be used as an input.

# 

# \## Ladder logic (current)

# 

# | Rung | Logic |

# | --- | --- |

# | 1 | beam\_clear AND pass\_flag -> green\_out |

# | 2 | beam\_clear AND fail\_flag -> red\_out |

# 

# So the light shows the laptop's result only when the operator's hand is out of the beam. While loading, both lights are off.

# 

# \## Communication (laptop <-> PLC)

# 

# | Setting | Value |

# | --- | --- |

# | Protocol | Modbus RTU over USB serial, PLC is the slave (server), laptop is the master (client) |

# | Port / speed | COM4, 115200 baud, 8N1, slave ID 1 |

# | OpenPLC setup | Servers -> Modbus server added and \*\*enabled\*\* (without it, every request returns exception 1, Illegal Function) |

# | Laptop reads | Function 2, discrete input 0 (beam\_clear), polled every loop |

# | Laptop writes | Function 15, coils 0 to 3 in one message: \[fail\_flag, False, False, pass\_flag] |

# 

# Coils 1 and 2 (green/red outputs) are rewritten by the ladder every 20 ms scan, so the laptop's False values there have no effect.

# 

# \## Breadboard wiring

# 

# | Item | From | To |

# | --- | --- | --- |

# | 5V supply | Arduino 5V | + rail, row 27 |

# | Ground | Arduino GND (next to pin 13) | - rail, row 15 |

# | Green light | Pin 7 | Row 10a, 220 ohm (10c to 14c), green LED (long leg 14a, short leg - rail) |

# | Red light | Pin 8 | Row 20a, 220 ohm (20c to 24c), red LED (long leg 24a, short leg - rail) |

# | Emitter | Red / black | + rail / - rail, row 29 |

# | Receiver power | Red / black | + rail / - rail, row 25 |

# | Receiver signal | White | Row 28a |

# | PLC input | Pin 2 | Row 28d |

# 

# \## Commissioning notes

# 

# \- The break-beam sensor received was a different model than designed for. It drives its own output, so no external pull-up is used. An extra 10 kOhm pull-up prevented the signal from going low.

# \- Fault isolation steps used: emitter checked with a phone camera (infrared visible), PLC input checked by forcing row 28 to ground, then the pull-up was removed.

# \- Modbus first returned Illegal Function for every request. A reply with an error code meant cable, speed and slave ID were fine; the fix was enabling the Modbus server in OpenPLC.

# \- After any program change, the program must be built and uploaded to the Arduino.

# \- The laptop has one USB port; a USB hub connects both the camera and the Arduino.


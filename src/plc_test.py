"""Result test: laptop sends PASS, then FAIL, then clears. Watch the stack light."""
import time

from pymodbus.client import ModbusSerialClient

PASS_COIL, FAIL_COIL = 3, 0  # %QX0.3 pass_flag, %QX0.0 fail_flag

client = ModbusSerialClient(port="COM4", baudrate=115200, timeout=1)
print("Connected:", client.connect())


def send(passed, failed, label):
    client.write_coil(PASS_COIL, passed, device_id=1)
    client.write_coil(FAIL_COIL, failed, device_id=1)
    print(label)
    time.sleep(4)


send(True, False, "PASS sent -> expect GREEN for 4 s")
send(False, True, "FAIL sent -> expect RED for 4 s")
send(False, False, "Cleared -> expect both OFF")
client.close()
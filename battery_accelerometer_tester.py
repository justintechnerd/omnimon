#!/usr/bin/env python
import struct
import smbus
import time

CW2015_ADDRESS = 0x62
CW2015_REG_VCELL = 0x02
CW2015_REG_SOC = 0x04
CW2015_REG_MODE = 0x0A

class BatteryTester:
    def __init__(self):
        self.bus = smbus.SMBus(1)

    def quick_start(self):
        """ Initialize CW2015 fuel gauge """
        try:
            self.bus.write_word_data(CW2015_ADDRESS, CW2015_REG_MODE, 0x30)
            time.sleep(1)  # Allow chip to calibrate
        except Exception as e:
            print(f"QuickStart error: {e}")

    def read_voltage(self):
        """ Read battery voltage """
        try:
            vcell = self.bus.read_word_data(CW2015_ADDRESS, CW2015_REG_VCELL)
            voltage = ((vcell & 0xFF) << 8 | (vcell >> 8)) * 0.305 / 1000
            return voltage
        except Exception as e:
            print(f"Voltage read error: {e}")
            return None

    def read_capacity(self):
        """ Read battery percentage """
        try:
            soc = self.bus.read_word_data(CW2015_ADDRESS, CW2015_REG_SOC)
            capacity = ((soc & 0xFF) << 8 | (soc >> 8)) / 256
            return capacity
        except Exception as e:
            print(f"Capacity read error: {e}")
            return None

    def test_battery(self):
        """ Run continuous battery monitoring """
        self.quick_start()  # Initialize fuel gauge

        while True:
            voltage = self.read_voltage()
            capacity = self.read_capacity()

            print("++++++++++++++++++++")
            print(f"?? Voltage: {voltage:.2f}V" if voltage else "Voltage Read Error")
            print(f"?? Battery: {capacity:.1f}%" if capacity else "Capacity Read Error")
            print("++++++++++++++++++++")

            time.sleep(2)

if __name__ == "__main__":
    tester = BatteryTester()
    tester.test_battery()
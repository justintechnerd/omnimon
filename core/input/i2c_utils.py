import time
import struct
import platform

# Detect if running on Raspberry Pi
IS_PI = platform.system() == "Linux" and platform.machine().startswith("arm")

if IS_PI:
    try:
        import RPi.GPIO as GPIO # type: ignore
    except ImportError:
        GPIO = None
else:
    GPIO = None

try:
    import smbus  # type: ignore
    IS_RPI = True
except ImportError:
    IS_RPI = False


class I2CUtils:
    def __init__(self):
        self.bus = smbus.SMBus(1) if IS_RPI else None
        self.battery_addr = 0x32
        self.bmi160_addr = 0x69
        self.valid = IS_RPI

        # Safe GPIO setup
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN)

        if IS_RPI:
            self.init_bmi160()

    def read_battery(self):
        try:
            vcell = self.bus.read_word_data(self.battery_addr, 0x02)
            soc = self.bus.read_word_data(self.battery_addr, 0x04)

            # Convert voltage and SOC
            voltage = ((vcell & 0xFF) << 8 | (vcell >> 8)) * 1.25 / 1000
            capacity_raw = (soc & 0xFF) << 8 | (soc >> 8)
            capacity = capacity_raw / 256.0

            return voltage, capacity
        except:
            return None, None

    def is_charging(self):
        if GPIO:
            return GPIO.input(4) == GPIO.HIGH
        return False

    def init_bmi160(self):
        try:
            self.bus.write_byte_data(self.bmi160_addr, 0x7E, 0xB6)
            time.sleep(0.1)
            self.bus.write_byte_data(self.bmi160_addr, 0x40, 0x28)
            self.bus.write_byte_data(self.bmi160_addr, 0x41, 0x03)
            self.bus.write_byte_data(self.bmi160_addr, 0x7E, 0x11)
            time.sleep(0.1)
        except Exception:
            self.valid = False

    def read_accel(self):
        if not self.valid:
            return 0.0, 0.0, 1.0  # Default Z-axis down
        try:
            data = self.bus.read_i2c_block_data(self.bmi160_addr, 0x12, 6)
            x = struct.unpack('<h', bytes(data[0:2]))[0]
            y = struct.unpack('<h', bytes(data[2:4]))[0]
            z = struct.unpack('<h', bytes(data[4:6]))[0]
            factor = 16384.0
            return x / factor, y / factor, z / factor
        except Exception:
            return None, None, None
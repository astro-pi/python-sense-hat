"""
Python library for the TCS34725 Color Sensor
Documentation (including datasheet): https://ams.com/tcs34725#tab/documents
"""

import smbus
import glob
from time import sleep


# device-specific constants
BUS = 1
ADDR = 0x29

COMMAND_BIT = 0x80

# control registers 
ENABLE = 0x00 | COMMAND_BIT
ATIME = 0x01 | COMMAND_BIT
CONTROL = 0x0F | COMMAND_BIT
ID = 0x12 | COMMAND_BIT
STATUS = 0x13 | COMMAND_BIT
# (if a register is described in the datasheet but missing here
# it means the corresponding functionality is not provided)

# data registers
CDATA = 0x14 | COMMAND_BIT
RDATA = 0x16 | COMMAND_BIT
GDATA = 0x18 | COMMAND_BIT
BDATA = 0x1A | COMMAND_BIT

# bit positions
PON = 0x01
AEN = 0x02
AVALID = 0x01

GAIN_MAP = {1: 0x00, 4: 0x01, 16: 0x02, 60: 0x03}  # maps gain values to register values
GAIN_INV = dict(zip(GAIN_MAP.values(), GAIN_MAP.keys()))

CLOCK_STEP = 0.0024 # the clock step is 2.4ms

_error_str = "Failed to initialise TCS34725 colour sensor."

def i2c_enabled():
    """Returns True if I2C is enabled or False otherwise."""
    return next(glob.iglob('/sys/bus/i2c/devices/*'), None) is not None

def _raw_wrapper(register):
    """
    Returns a function that retrieves the sensor reading at `register`.
    The CRGB readings are all retrieved from the sensor in an identical fashion.
    This is a factory function that implements this retrieval method.
    """
    def get_raw(self):
        value = self.bus.read_word_data(ADDR, register)
        return value
    return get_raw

def _byte_wrapper(register):
    """
    Returns a function that retrieves the sensor reading at `register`, scaled to 0-255.
    The CRGB readings are all retrieved from the sensor in an identical fashion.
    This is a factory function that implements this retrieval method.
    """
    def get_byte(self):
        value = self.bus.read_word_data(ADDR, register) // self._scaling
        return value
    return get_byte


class ColourSensor:
    
    def __init__(self, gain=1, integration_cycles=1):
        try:
            self.bus = smbus.SMBus(BUS)
        except Exception as e:
            explanation = " (I2C is not enabled)" if not i2c_enabled() else ""
            raise RuntimeError(f'{_error_str}{explanation}') from e
        
        try:
            id = self.bus.read_byte_data(ADDR, ID)
        except Exception as e:
            explanation = " (sensor not present)"
            raise RuntimeError(f'{_error_str}{explanation}') from e

        if id != 0x44:
            explanation = f" (different device id detected: {id})"
            raise RuntimeError(f'{_error_str}{explanation}')

        self.gain = gain
        self.integration_cycles=integration_cycles
        self.enabled = 1

    @property
    def enabled(self):
        return self.bus.read_byte_data(ADDR, ENABLE) == (PON | AEN)

    @enabled.setter
    def enabled(self, status):
        if status:
            self.bus.write_byte_data(ADDR, ENABLE, PON)
            sleep(CLOCK_STEP) # From datasheet: "there is a 2.4 ms warm-up delay if PON is enabled."
            self.bus.write_byte_data(ADDR, ENABLE, (PON | AEN))
        else:
            self.bus.write_byte_data(ADDR, ENABLE, 0x00)
        sleep(CLOCK_STEP)

    @property
    def gain(self):
        return GAIN_INV[self.bus.read_byte_data(ADDR, CONTROL)]

    @gain.setter
    def gain(self, value):
        if value in GAIN_MAP:
            self.bus.write_byte_data(ADDR, CONTROL, GAIN_MAP[value])
            sleep(CLOCK_STEP)
        else:
            raise RuntimeError(f'Cannot set gain to {value}. Values: {tuple(GAIN_MAP.keys())}')

    @property
    def integration_cycles(self):
        return 256 - self.bus.read_byte_data(ADDR, ATIME)

    @integration_cycles.setter
    def integration_cycles(self, cycles):
        if 1 <= cycles <= 256:
            self.bus.write_byte_data(ADDR, ATIME, 256-cycles)
            self._integration_time = cycles * CLOCK_STEP
            self._max_value = 2**16 if cycles >= 64 else 1024*cycles
            self._scaling = self._max_value // 256
            sleep(CLOCK_STEP)
        else:
            raise RuntimeError(f'Cannot set integration cycles to {cycles} (1-256)')

    @property
    def integration_time(self):
        return self._integration_time

    @property
    def max_raw(self):
        return self._max_value

    @property
    def colour_raw(self):
        block = self.bus.read_i2c_block_data(ADDR, CDATA, 8)
        return (
            (block[3] << 8) + block[2],
            (block[5] << 8) + block[4],
            (block[7] << 8) + block[6],
            (block[1] << 8) + block[0]
        )

    @property
    def colour(self):
        return tuple(reading // self._scaling for reading in self.colour_raw)

    color_raw = colour_raw
    red_raw = property(_raw_wrapper(RDATA))
    green_raw = property(_raw_wrapper(GDATA))
    blue_raw = property(_raw_wrapper(BDATA))
    clear_raw = property(_raw_wrapper(CDATA))

    color = colour
    red = property(_byte_wrapper(RDATA))
    green = property(_byte_wrapper(GDATA))
    blue = property(_byte_wrapper(BDATA))
    clear = property(_byte_wrapper(CDATA))

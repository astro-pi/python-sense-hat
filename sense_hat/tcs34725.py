"""
Python library for the TCS34725 Color Sensor

Documentation (including datasheet): https://ams.com/tcs34725#tab/documents
"""

import smbus
import glob
from time import sleep

def i2c_enabled():
    return next(glob.iglob('/sys/bus/i2c/devices/*'), None) is not None

class TCS34725:
    
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

    def __init__(self, gain=1, integration_cycles=1):
        try:
            self.bus = smbus.SMBus(self.BUS)
        except Exception:
            explanation = " (I2C is not enabled)" if not i2c_enabled() else ""
            raise RuntimeError(f'Failed to initialise TCS34725 colour sensor.{explanation}')
        else:
            if self._id != 0x44:
                raise RuntimeError(f'Not connected to TCS34725 (id: {self._id})')
            self.gain = gain
            self.integration_cycles=integration_cycles
            self.enabled= 1

    @property
    def _id(self):
        return self.bus.read_byte_data(self.ADDR, self.ID)

    @property
    def enabled(self):
        return self.bus.read_byte_data(self.ADDR, self.ENABLE) == (self.PON | self.AEN)

    @enabled.setter
    def enabled(self, status):
        if status:
            self.bus.write_byte_data(self.ADDR, (self.ENABLE), self.PON)
            sleep(self.CLOCK_STEP) # From datasheet: "there is a 2.4 ms warm-up delay if PON is enabled."
            self.bus.write_byte_data(self.ADDR, (self.ENABLE), (self.PON | self.AEN))
        else:
            self.bus.write_byte_data(self.ADDR, (self.ENABLE), 0x00)
        sleep(self.CLOCK_STEP)

    @property
    def gain(self):
        return self.GAIN_INV[self.bus.read_byte_data(self.ADDR, self.CONTROL)]

    @gain.setter
    def gain(self, value):
        if value in self.GAIN_MAP:
            self.bus.write_byte_data(self.ADDR, self.CONTROL, self.GAIN_MAP[value])
            sleep(self.CLOCK_STEP)
        else:
            raise RuntimeError(f'Cannot set gain to {value}. {tuple(self.GAIN_MAP.keys())}')

    @property
    def integration_cycles(self):
        return 256 - self.bus.read_byte_data(self.ADDR, self.ATIME)

    @integration_cycles.setter
    def integration_cycles(self, cycles):
        if 1 <= cycles <= 256:
            self.bus.write_byte_data(self.ADDR, self.ATIME, 256-cycles)
            self.integration_time = cycles * self.CLOCK_STEP
            self.max_value = 2**16 if cycles >= 64 else 1024*cycles
            self._scaling = self.max_value // 256
            sleep(self.CLOCK_STEP)
        else:
            raise RuntimeError(f'Cannot set integration cycles to {cycles} (1-256)')

    @property
    def colour_raw(self):
        block = self.bus.read_i2c_block_data(self.ADDR, self.CDATA, 8)
        return (
            (block[3] << 8) + block[2],
            (block[5] << 8) + block[4],
            (block[7] << 8) + block[6],
            (block[1] << 8) + block[0]
        )

    @property
    def colour(self):
        return tuple(reading // self._scaling for reading in self.colour_raw)

    @staticmethod
    def _raw_wrapper(register):
        """
        Returns a function that retrieves the sensor reading at `register`.
        The CRGB readings are all retrieved from the sensor in an identical fashion.
        This is a factory function that implements this retrieval method.
        """
        def get_raw(self):
            value = self.bus.read_word_data(self.ADDR, register)
            return value
        return get_raw

    clear_raw = property(_raw_wrapper(CDATA))
    red_raw = property(_raw_wrapper(RDATA))
    green_raw = property(_raw_wrapper(GDATA))
    blue_raw = property(_raw_wrapper(BDATA))

    @staticmethod
    def _byte_wrapper(register):
        """
        Returns a function that retrieves the sensor reading at `register`, scaled to 0-255.
        The CRGB readings are all retrieved from the sensor in an identical fashion.
        This is a factory function that implements this retrieval method.
        """
        def get_byte(self):
            value = self.bus.read_word_data(self.ADDR, register) // self._scaling
            return value
        return get_byte

    clear = property(_byte_wrapper(CDATA))
    red = property(_byte_wrapper(RDATA))
    green = property(_byte_wrapper(GDATA))
    blue = property(_byte_wrapper(BDATA))

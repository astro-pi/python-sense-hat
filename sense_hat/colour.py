"""
Python library for the TCS34725 Color Sensor
Documentation (including datasheet): https://ams.com/tcs34725#tab/documents
"""

import smbus
import glob

import io, os, sys, errno
import mmap
from struct import Struct
from collections import namedtuple

from time import sleep

_error_str = "Failed to initialise TCS34725 colour sensor."

class HardwareInterface:

    GAIN_VALUES = (1, 4, 16, 60)
    CLOCK_STEP = 0.0024 # the clock step is 2.4ms

    def get_enabled(self):
        raise NotImplementedError

    def set_enabled(self, value):
        raise NotImplementedError

    def get_gain(self):
        raise NotImplementedError

    def set_gain(self, value):
        raise NotImplementedError

    def get_integration_cycles(self):
        raise NotImplementedError

    def set_integration_cycles(self, value):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError

    def get_red(self):
        raise NotImplementedError

    def get_green(self):
        raise NotImplementedError

    def get_blue(self):
        raise NotImplementedError

    def get_clear(self):
        raise NotImplementedError


def _raw_wrapper(register):
    """
    Returns a function that retrieves the sensor reading at `register`.
    The CRGB readings are all retrieved from the sensor in an identical fashion.
    This is a factory function that implements this retrieval method.
    """
    def get_raw(self):
        return self.read(register)
    return get_raw

class I2C(HardwareInterface):

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
    OFF = 0x00
    PON = 0x01
    AEN = 0x02
    ON = (PON | AEN)
    AVALID = 0x01

    GAIN_REG_VALUES = (0x00, 0x01, 0x02, 0x03)
    GAIN_TO_REG = dict(zip(HardwareInterface.GAIN_VALUES, GAIN_REG_VALUES)) # maps gain values to register values
    REG_TO_GAIN = dict(zip(GAIN_REG_VALUES, HardwareInterface.GAIN_VALUES))

    def __init__(self):

        try:
            self.bus = smbus.SMBus(self.BUS)
        except Exception as e:
            explanation = " (I2C is not enabled)" if not self.i2c_enabled() else ""
            raise RuntimeError(f'{_error_str}{explanation}') from e
        
        try:
            id = self.read(self.ID)
        except Exception as e:
            explanation = " (sensor not present)"
            raise RuntimeError(f'{_error_str}{explanation}') from e

        if id != 0x44:
            explanation = f" (different device id detected: {id})"
            raise RuntimeError(f'{_error_str}{explanation}')

    @staticmethod
    def i2c_enabled():
        """Returns True if I2C is enabled or False otherwise."""
        return next(glob.iglob('/sys/bus/i2c/devices/*'), None) is not None

    def read(self, attribute):
        return self.bus.read_byte_data(self.ADDR, attribute)
    
    def write(self, attribute, value):
        self.bus.write_byte_data(self.ADDR, attribute, value)

    def get_enabled(self):
        return self.read(self.ENABLE) == (PON | AEN)

    def set_enabled(self, value):
        if value:
            self.write(self.ENABLE, self.PON)
            sleep(self.CLOCK_STEP) # From datasheet: "there is a 2.4 ms warm-up delay if PON is enabled."
            self.write(self.ENABLE, self.ON)
        else:
            self.write(self.ENABLE, self.OFF)
        sleep(self.CLOCK_STEP)

    def get_gain(self):
        register_value = self.read(self.CONTROL)
        return self.REG_TO_GAIN[register_value]

    def set_gain(self, value):
        register_value = self.GAIN_TO_REG[value]
        self.write(self.CONTROL, register_value)

    def get_integration_cycles(self):
        return 256 - self.read(self.ATIME)

    def set_integration_cycles(self, value):
        self.write(self.ATIME, 256-value)

    def get_all(self):
        block = self.bus.read_i2c_block_data(self.ADDR, self.CDATA, 8)
        return (
            (block[3] << 8) + block[2],
            (block[5] << 8) + block[4],
            (block[7] << 8) + block[6],
            (block[1] << 8) + block[0]
        )

    get_red = _raw_wrapper(RDATA)
    get_green = _raw_wrapper(GDATA)
    get_blue = _raw_wrapper(BDATA)
    get_clear = _raw_wrapper(CDATA)


class StatusFile(HardwareInterface):

    COLOUR_DATA = Struct(str(
        '@'   # native mode
        '?'   # enabled
        '4I'  # RGBC
        'H'   # gain
        'H'   # integration cycles
        ))

    ColourData = namedtuple(
        'ColourData', (
            'enabled', 'R', 'G', 'B', 'C', 'gain', 'integration_cycles'))

    def __init__(self):
        self.init_file()

    @staticmethod
    def filename():
        """
        Return the filename used to represent the state of the emulated sense HAT's
        co sensor. On UNIX we try ``/dev/shm`` then fall back to ``/tmp``; on
        Windows we use whatever ``%TEMP%`` contains
        """
        fname = 'rpi-sense-emu-colour'
        if sys.platform.startswith('win'):
            # just use a temporary file on Windows
            return os.path.join(os.environ['TEMP'], fname)
        else:
            if os.path.exists('/dev/shm'):
                return os.path.join('/dev/shm', fname)
            else:
                return os.path.join('/tmp', fname)

    def init_file(self):
        """
        Opens the file representing the state of the humidity sensor. The
        file-like object is returned.
        If the file already exists we simply make sure it is the right size. If
        the file does not already exist, it is created and zeroed.
        """
        try:
            # Attempt to open the colour sensor's file and ensure it's the right size
            fd = io.open(self.filename(), 'r+b', buffering=0)
            fd.seek(self.COLOUR_DATA.size)
            fd.truncate()
        except IOError as e:
            # If the colour sensor device file doesn't exist, zero it into existence
            if e.errno == errno.ENOENT:
                fd = io.open(self.filename(), 'w+b', buffering=0)
                fd.write(b'\x00' * self.COLOUR_DATA.size)
            else:
                raise IOError from e
        else:
            self._fd = fd
            self._map = mmap.mmap(self._fd.fileno(), 0, access=mmap.ACCESS_WRITE)

    def read(self):
        return self.ColourData(*self.COLOUR_DATA.unpack_from(self._map))

    def write(self, value):
        self.COLOUR_DATA.pack_into(self._map, 0, *value)

    def get_enabled(self):
        return self.read().enabled

    def set_enabled(self, value):
        self.write(self.read()._replace(enabled=value))

    def get_gain(self):
        return self.read().gain

    def set_gain(self, value):
        self.write(self.read()._replace(gain=value))

    def get_integration_cycles(self):
        return self.read().integration_cycles

    def set_integration_cycles(self, value):
        self.write(self.read()._replace(integration_cycles=value))

    def get_all(self):
        _, R, G, B, C, _, _ = self.read()
        return (R, G, B, C)

    def get_red(self):
        print(f"DEBUG: {self.read()}")
        return self.read().R

    def get_green(self):
        return self.read().G

    def get_blue(self):
        return self.read().B

    def get_clear(self):
        return self.read().C


class ColourSensor:
    
    def __init__(self, gain=1, integration_cycles=1, interface=I2C):
        self.interface = interface()
        self.gain = gain
        self.integration_cycles = integration_cycles
        self.enabled = 1

    @property
    def enabled(self):
        return self.interface.get_enabled()

    @enabled.setter
    def enabled(self, status):
        self.interface.set_enabled(status)

    @property
    def gain(self):
        return self.interface.get_gain()

    @gain.setter
    def gain(self, value):
        if value in self.interface.GAIN_VALUES:
            self.interface.set_gain(value)
        else:
            raise RuntimeError(f'Cannot set gain to {value}. Values: {self.interface.GAIN_VALUES}')

    @property
    def integration_cycles(self):
        return self.interface.get_integration_cycles()

    @integration_cycles.setter
    def integration_cycles(self, cycles):
        if 1 <= cycles <= 256:
            self.interface.set_integration_cycles(cycles)
            self._integration_time = cycles * self.interface.CLOCK_STEP
            self._max_value = 2**16 if cycles >= 64 else 1024*cycles
            self._scaling = self._max_value // 256
            sleep(self.interface.CLOCK_STEP)
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
        return self.interface.get_all()

    @property
    def colour(self):
        return tuple(reading // self._scaling for reading in self.colour_raw)

    color_raw = colour_raw
    color = colour

    # For the following, could also use something like:
    # red_raw = property(lambda self: self.interface.get_red())

    @property
    def red_raw(self):
        return self.interface.get_red()
    
    @property
    def green_raw(self):
        return self.interface.get_green()

    @property
    def blue_raw(self):
        return self.interface.get_blue()

    @property
    def clear_raw(self):
        return self.interface.get_clear()

    @property
    def red(self):
        return self.red_raw // self._scaling
    
    @property
    def green(self):
        return self.green_raw // self._scaling

    @property
    def blue(self):
        return self.blue_raw // self._scaling

    @property
    def clear(self):
        return self.clear_raw // self._scaling
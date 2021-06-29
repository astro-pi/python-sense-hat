"""
Python library for the TCS34725 Color Sensor
Documentation (including datasheet): https://ams.com/tcs34725#tab/documents
"""

from time import sleep

_error_str = "Failed to initialise TCS34725 colour sensor."


class HardwareInterface:
    """
    `HardwareInterface` is the abstract class that sits between the
    `ColourSensor` class (providing the TCS34725 sensor API) and the
    actual hardware. Using this intermediate layer of abstraction, a
    `ColourSensor` object interacts with the hardware without being
    aware of how this interaction is implemented.

    Different subclasses of the `HardwareInterface` class can provide
    access to the hardware through e.g. I2C, `libiio` and its system
    files or even a hardware emulator.
    """

    GAIN_VALUES = (1, 4, 16, 60)
    CLOCK_STEP = 0.0024 # the clock step is 2.4ms

    @staticmethod
    def max_value(integration_cycles):
        """
        The maximum raw value for the RBGC channels depends on the number
        of integration cycles.
        """
        return 2**16 if integration_cycles >= 64 else 1024*integration_cycles

    def get_enabled(self):
        """
        Return True if the sensor is enabled and False otherwise
        """
        raise NotImplementedError

    def set_enabled(self, status):
        """
        Enable or disable the sensor, depending on the boolean `status` flag
        """
        raise NotImplementedError

    def get_gain(self):
        """
        Return the current value of the sensor gain.
        See GAIN_VALUES for the set of possible values.
        """
        raise NotImplementedError

    def set_gain(self, gain):
        """
        Set the value for the sensor `gain`.
        See GAIN_VALUES for the set of possible values.
        """
        raise NotImplementedError

    def get_integration_cycles(self):
        """
        Return the current number of integration_cycles (1-256).
        It takes `integration_cycles` * CLOCK_STEP to obtain a new
        sensor reading.
        """
        raise NotImplementedError

    def set_integration_cycles(self, integration_cycles):
        """
        Set the current number of integration_cycles (1-256).
        It takes `integration_cycles` * CLOCK_STEP to obtain a new
        sensor reading.
        """
        raise NotImplementedError

    def get_raw(self):
        """
        Return a tuple containing the raw values of the RGBC channels.
        The maximum for these raw values depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_red(self):
        """
        Return a the raw value of the R (red) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_green(self):
        """
        Return a the raw value of the G (green) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_blue(self):
        """
        Return a the raw value of the B (blue) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_clear(self):
        """
        Return a the raw value of the C (clear light) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError


### An I2C implementation of the abstract colour sensor `HardwareInterface`

def _raw_wrapper(register):
    """
    Returns a function that retrieves the sensor reading at `register`.
    The RGBC readings are all retrieved from the sensor in an identical
    fashion. This is a factory function that implements this retrieval method.
    """
    def get_raw_register(self):
        return self._read(register)
    return get_raw_register

class I2C(HardwareInterface):
    """
    An implementation of the `HardwareInterface` for the TCS34725 sensor
    that uses I2C to control the sensor and retrieve measurements.

    Use the datasheet as a reference: https://ams.com/tcs34725#tab/documents
    """

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
    # map gain values to register values and vice-versa
    GAIN_TO_REG = dict(zip(HardwareInterface.GAIN_VALUES, GAIN_REG_VALUES))
    REG_TO_GAIN = dict(zip(GAIN_REG_VALUES, HardwareInterface.GAIN_VALUES))

    def __init__(self):

        import smbus
        import glob

        try:
            self.bus = smbus.SMBus(self.BUS)
        except Exception as e:
            explanation = " (I2C is not enabled)" if not self.i2c_enabled() else ""
            raise RuntimeError(f'{_error_str}{explanation}') from e
        
        try:
            id = self._read(self.ID)
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

    def _read(self, attribute):
        """
        Read and return the value of a specific register (`attribute`) of the
        TCS34725 colour sensor.
        """
        return self.bus.read_byte_data(self.ADDR, attribute)
    
    def _write(self, attribute, value):
        """
        Write a value in a specific register (`attribute`) of the
        TCS34725 colour sensor.
        """
        self.bus.write_byte_data(self.ADDR, attribute, value)

    def get_enabled(self):
        """
        Return True if the sensor is enabled and False otherwise
        """
        return self._read(self.ENABLE) == (PON | AEN)

    def set_enabled(self, status):
        """
        Enable or disable the sensor, depending on the boolean `status` flag
        """
        if status:
            self._write(self.ENABLE, self.PON)
            sleep(self.CLOCK_STEP) # From datasheet: "there is a 2.4 ms warm-up delay if PON is enabled."
            self._write(self.ENABLE, self.ON)
        else:
            self._write(self.ENABLE, self.OFF)
        sleep(self.CLOCK_STEP)

    def get_gain(self):
        """
        Return the current value of the sensor gain.
        See GAIN_VALUES for the set of possible values.
        """
        register_value = self._read(self.CONTROL)
        # map the register value to an actual gain value
        return self.REG_TO_GAIN[register_value]

    def set_gain(self, gain):
        """
        Set the value for the sensor `gain`.
        See GAIN_VALUES for the set of possible values.
        """
        # map the specified value for `gain` to a register value
        register_value = self.GAIN_TO_REG[gain]
        self._write(self.CONTROL, register_value)

    def get_integration_cycles(self):
        """
        Return the current number of integration_cycles (1-256).
        It takes `integration_cycles` * CLOCK_STEP to obtain a new
        sensor reading.
        """
        return 256 - self._read(self.ATIME)

    def set_integration_cycles(self, integration_cycles):
        """
        Set the current number of integration_cycles (1-256).
        It takes `integration_cycles` * CLOCK_STEP to obtain a new
        sensor reading.
        """
        self._write(self.ATIME, 256-integration_cycles)

    def get_raw(self):
        """
        Return a tuple containing the raw values of the RGBC channels.
        The maximum for these raw values depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        # The 4-tuple is retrieved using a *single read*.
        block = self.bus.read_i2c_block_data(self.ADDR, self.CDATA, 8)
        return (
            (block[3] << 8) + block[2],
            (block[5] << 8) + block[4],
            (block[7] << 8) + block[6],
            (block[1] << 8) + block[0]
        )

    """
    The methods below return the raw value of the R, G, B or Clear channels.
    The maximum for these raw value depends on the number of integration
    cycles and can be computed using `max_value`.
    Use these methods if you only make use of one channel reading per iteration.
    Otherwise, you are probably better off using `get_raw`, to retrieve all
    channels in a single read.
    """
    get_red = _raw_wrapper(RDATA)
    get_green = _raw_wrapper(GDATA)
    get_blue = _raw_wrapper(BDATA)
    get_clear = _raw_wrapper(CDATA)


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
    def gain(self, gain):
        if gain in self.interface.GAIN_VALUES:
            self.interface.set_gain(gain)
        else:
            raise ValueError(f'Cannot set gain to {gain}. Values: {self.interface.GAIN_VALUES}')

    @property
    def integration_cycles(self):
        return self.interface.get_integration_cycles()

    @integration_cycles.setter
    def integration_cycles(self, integration_cycles):
        if 1 <= integration_cycles <= 256:
            self.interface.set_integration_cycles(integration_cycles)
            self._integration_time = integration_cycles * self.interface.CLOCK_STEP
            self._max_value = self.interface.max_value(integration_cycles)
            self._scaling = self._max_value // 256
            sleep(self.interface.CLOCK_STEP)
        else:
            raise ValueError(f'Cannot set integration cycles to {integration_cycles} (1-256)')

    @property
    def integration_time(self):
        return self._integration_time

    @property
    def max_raw(self):
        return self._max_value

    @property
    def colour_raw(self):
        return self.interface.get_raw()

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
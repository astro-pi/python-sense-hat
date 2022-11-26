"""
Python library for the TCS3472x and TCS340x Color Sensors
Documentation (including datasheet): https://ams.com/tcs34725#tab/documents
                                     https://ams.com/tcs3400#tab/documents
The sense hat for AstroPi on the ISS uses the TCS34725.
The sense hat v2 uses the TCS3400 the successor of the TCS34725.
The TCS34725 is not available any more. It was discontinued by ams in 2021.
"""

from time import sleep
from .exceptions import ColourSensorInitialisationError, InvalidGainError, \
    InvalidIntegrationCyclesError


class HardwareInterface:
    """
    `HardwareInterface` is the abstract class that sits between the
    `ColourSensor` class (providing the TCS34725/TCS3400 sensor API)
    and the actual hardware. Using this intermediate layer of abstraction,
    a `ColourSensor` object interacts with the hardware without being
    aware of how this interaction is implemented.
    Different subclasses of the `HardwareInterface` class can provide
    access to the hardware through e.g. I2C, `libiio` and its system
    files or even a hardware emulator.
    """

    @staticmethod
    def max_value(integration_cycles):
        """
        The maximum raw value for the RBGC channels depends on the number
        of integration cycles.
        """
        return 65535 if integration_cycles >= 64 else 1024*integration_cycles

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
        Return the raw value of the R (red) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_green(self):
        """
        Return the raw value of the G (green) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_blue(self):
        """
        Return the raw value of the B (blue) channel.
        The maximum for this raw value depends on the number of
        integration cycles and can be computed using `max_value`.
        """
        raise NotImplementedError

    def get_clear(self):
        """
        Return the raw value of the C (clear light) channel.
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
        block = self.bus.read_i2c_block_data(self.ADDR, register, 2)
        return (block[0] + (block[1] << 8))
    return get_raw_register

class I2C(HardwareInterface):
    """
    An implementation of the `HardwareInterface` for the TCS34725/TCS3400
    sensor that uses I2C to control the sensor and retrieve measurements.
    Use the datasheets as a reference.
    """

    # device-specific constants
    BUS = 1

    # control registers 
    ENABLE = 0x80
    ATIME = 0x81
    CONTROL = 0x8F
    ID = 0x92
    STATUS = 0x93
    # (if a register is described in the datasheet but missing here
    # it means the corresponding functionality is not provided)

    # data registers
    CDATA = 0x94
    RDATA = 0x96
    GDATA = 0x98
    BDATA = 0x9A

    # bit positions
    OFF = 0x00
    PON = 0x01
    AEN = 0x02
    ON = (PON | AEN)
    AVALID = 0x01

    GAIN_REG_VALUES = (0x00, 0x01, 0x02, 0x03)
    # Assume TCS34725 as on the ISS AstroPi
    # Adjust for TCS3400 after the detection of the sensor type.
    ADDR = 0x29
    GAIN_VALUES = (1, 4, 16, 60)
    CLOCK_STEP = 0.0024 # 2.4ms
    GAIN_TO_REG = dict(zip(GAIN_VALUES, GAIN_REG_VALUES))
    REG_TO_GAIN = dict(zip(GAIN_REG_VALUES, GAIN_VALUES))

    def __init__(self):

        import smbus
        import glob

        try:
            self.bus = smbus.SMBus(self.BUS)
        except Exception as e:
            explanation = "(I2C is not enabled)" if not self.i2c_enabled() else ""
            raise ColourSensorInitialisationError(explanation=explanation) from e

        # Test for sensor at I2C addresses 0x29 or 0x39
        # Both sensors have variants at 0x29 and 0x39 (See data sheets)
        addr1 = addr2 = False
        try:
            self.bus.write_quick(0x29)
            addr1 = True
        except:
            pass
        try:
            self.bus.write_quick(0x39)
            addr2 = True
        except:
            pass

        if addr2:
            self.ADDR = 0x39
        if addr1 or addr2:
            # get sensor id
            id = self._read(self.ID)
            if (id & 0xf8) == 0x90:
                sensor = 'TCS340x'
            elif (id & 0xf4) == 0x44:
                sensor = 'TCS3472x'
        else:
            explanation = "(Sensor not present)"
            raise ColourSensorInitialisationError(explanation=explanation)

        # Set type specific constants
        # Assume TCS3472x as in AstroPi
        sensor == 'TCS3472x'
        if sensor == 'TCS340x':
            self.GAIN_VALUES = (1, 4, 16, 64)
            self.CLOCK_STEP = 0.00275 # 2.75ms
            self.GAIN_TO_REG = dict(zip(self.GAIN_VALUES, self.GAIN_REG_VALUES))
            self.REG_TO_GAIN = dict(zip(self.GAIN_REG_VALUES, self.GAIN_VALUES))

    @staticmethod
    def i2c_enabled():
        """Returns True if I2C is enabled or False otherwise."""
        return next(glob.iglob('/sys/bus/i2c/devices/*'), None) is not None

    def _read(self, attribute):
        """
        Read and return the value of a specific register (`attribute`) of the
        TCS34725/TCS3400 colour sensor.
        """
        return self.bus.read_byte_data(self.ADDR, attribute)
    
    def _write(self, attribute, value):
        """
        Write a value in a specific register (`attribute`) of the
        TCS34725/TCS3400 colour sensor.
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
            raise InvalidGainError(gain=gain, values=self.interface.GAIN_VALUES)

    @property
    def integration_cycles(self):
        return self.interface.get_integration_cycles()

    @integration_cycles.setter
    def integration_cycles(self, integration_cycles):
        if 1 <= integration_cycles <= 256:
            self.interface.set_integration_cycles(integration_cycles)
            sleep(self.interface.CLOCK_STEP)
        else:
            raise InvalidIntegrationCyclesError(integration_cycles=integration_cycles)

    @property
    def integration_time(self):
        return self.integration_cycles * self.interface.CLOCK_STEP

    @property
    def max_raw(self):
        return self.interface.max_value(self.integration_cycles)

    @property
    def colour_raw(self):
        return self.interface.get_raw()

    color_raw = colour_raw
    red_raw = property(lambda self: self.interface.get_red())
    green_raw = property(lambda self: self.interface.get_green())
    blue_raw = property(lambda self: self.interface.get_blue())
    clear_raw = property(lambda self: self.interface.get_clear())
    brightness = clear_raw

    @property
    def _scaling(self):
        return self.max_raw // 256
    
    @property
    def colour(self):
        return tuple(reading // self._scaling for reading in self.colour_raw)

    @property
    def rgb(self):
        return tuple(reading // self._scaling for reading in self.colour_raw)[0:3]

    color = colour
    red = property(lambda self: self.red_raw // self._scaling )
    green = property(lambda self: self.green_raw // self._scaling )
    blue = property(lambda self: self.blue_raw // self._scaling )
    clear = property(lambda self: self.clear_raw // self._scaling )

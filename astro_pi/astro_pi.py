#!/usr/bin/python
import struct
import os
import sys
import math
import time
import numpy as np
import RTIMU  # custom version
from PIL import Image  # pillow


class AstroPi(object):
    def __init__(
            self,
            fb_device='/dev/fb1',
            imu_settings_file='RTIMULib',
            text_assets='astro_pi_text'
        ):

        self._fb_device = fb_device

        # 0 is With B+ HDMI port facing downwards
        pix_map0 = np.array([
             [0,  1,  2,  3,  4,  5,  6,  7],
             [8,  9, 10, 11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20, 21, 22, 23],
            [24, 25, 26, 27, 28, 29, 30, 31],
            [32, 33, 34, 35, 36, 37, 38, 39],
            [40, 41, 42, 43, 44, 45, 46, 47],
            [48, 49, 50, 51, 52, 53, 54, 55],
            [56, 57, 58, 59, 60, 61, 62, 63]
        ], int)

        pix_map90 = np.rot90(pix_map0)
        pix_map180 = np.rot90(pix_map90)
        pix_map270 = np.rot90(pix_map180)

        self._pix_map = {
              0: pix_map0,
             90: pix_map90,
            180: pix_map180,
            270: pix_map270
        }

        self._rotation = 0

        # Load text assets
        dir_path = os.path.dirname(__file__)
        self._load_text_assets(
            os.path.join(dir_path, '%s.png' % text_assets),
            os.path.join(dir_path, '%s.txt' % text_assets)
        )

        # Load IMU settings and calibration data
        self._imu_settings = RTIMU.Settings(imu_settings_file)
        self._imu = RTIMU.RTIMU(self._imu_settings)
        self._imu_init = False  # Will be initialised as and when needed
        self._pressure = RTIMU.RTPressure(self._imu_settings)
        self._pressure_init = False  # Will be initialised as and when needed
        self._humidity = RTIMU.RTHumidity(self._imu_settings)
        self._humidity_init = False  # Will be initialised as and when needed
        self._last_orientation = {'pitch': 0, 'roll': 0, 'yaw': 0}
        raw = {'x': 0, 'y': 0, 'z': 0}
        self._last_compass_raw = raw
        self._last_gyro_raw = raw
        self._last_accel_raw = raw
        self._compass_enabled = False
        self._gyro_enabled = False
        self._accel_enabled = False

    ####
    # Text assets
    ####

    # Text asset files are rotated right through 90 degrees to allow blocks of
    # 40 contiguous pixels to represent one 5 x 8 character. These are stored
    # in a 8 x 640 pixel png image with characters arranged adjacently
    # Consequently we must rotate the pixel map left through 90 degrees to
    # compensate when drawing text

    def _load_text_assets(self, text_image_file, text_file):
        """
        Internal. Builds a character indexed dictionary of pixels used by the
        show_message function below
        """

        text_pixels = self.load_image(text_image_file, False)
        with open(text_file, 'r') as f:
            loaded_text = f.read()
        self._text_dict = {}
        for index, s in enumerate(loaded_text):
            start = index * 40
            end = start + 40
            char = text_pixels[start:end]
            self._text_dict[s] = char

    def _trim_whitespace(self, char):  # For loading text assets only
        """
        Internal. Trims white space pixels from the front and back of loaded
        text characters
        """

        psum = lambda x: sum(sum(x, []))
        if psum(char) > 0:
            is_empty = True
            while is_empty:  # From front
                row = char[0:8]
                is_empty = psum(row) == 0
                if is_empty:
                    del char[0:8]
            is_empty = True
            while is_empty:  # From back
                row = char[-8:]
                is_empty = psum(row) == 0
                if is_empty:
                    del char[-8:]
        return char

    ####
    # LED Matrix
    ####

    def set_rotation(self, r=0, redraw=True):
        """
        Sets the LED matrix rotation for viewing, adjust if the Pi is upside
        down or sideways. 0 is with the Pi HDMI port facing downwards
        """

        if r in self._pix_map.keys():
            if redraw:
                pixel_list = self.get_pixels()
            self._rotation = r
            if redraw:
                self.set_pixels(pixel_list)
        else:
            raise ValueError('Rotation must be 0, 90, 180 or 270 degrees')

    def _pack_bin(self, pix):
        """
        Internal. Encodes python list [R,G,B] into 16 bit RGB565
        """

        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        bits16 = (r << 11) + (g << 5) + b
        return struct.pack('H', bits16)

    def _unpack_bin(self, packed):
        """
        Internal. Decodes 16 bit RGB565 into python list [R,G,B]
        """

        output = struct.unpack('H', packed)
        bits16 = output[0]
        r = (bits16 & 0xF800) >> 11
        g = (bits16 & 0x7E0) >> 5
        b = (bits16 & 0x1F)
        return [int(r << 3), int(g << 2), int(b << 3)]

    def flip_h(self, redraw=True):
        """
        Flip LED matrix horizontal
        """

        pixel_list = self.get_pixels()
        flipped = []
        for i in range(8):
            offset = i * 8
            flipped.extend(reversed(pixel_list[offset:offset + 8]))
        if redraw:
            self.set_pixels(flipped)
        return flipped

    def flip_v(self, redraw=True):
        """
        Flip LED matrix vertical
        """

        pixel_list = self.get_pixels()
        flipped = []
        for i in reversed(range(8)):
            offset = i * 8
            flipped.extend(pixel_list[offset:offset + 8])
        if redraw:
            self.set_pixels(flipped)
        return flipped

    def set_pixels(self, pixel_list):
        """
        Accepts a list containing 64 smaller lists of [R,G,B] pixels and
        updates the LED matrix. R,G,B elements must intergers between 0
        and 255
        """

        if len(pixel_list) != 64:
            raise ValueError('Pixel lists must have 64 elements')

        for index, pix in enumerate(pixel_list):
            if len(pix) != 3:
                raise ValueError('Pixel at index %d is invalid. Pixels must contain 3 elements: Red, Green and Blue' % index)

            for element in pix:
                if element > 255 or element < 0:
                    raise ValueError('Pixel at index %d is invalid. Pixel elements must be between 0 and 255' % index)

        with open(self._fb_device, 'wb') as f:
            map = self._pix_map[self._rotation]
            for index, pix in enumerate(pixel_list):
                # Two bytes per pixel in fb memory, 16 bit RGB565
                f.seek(map[index // 8][index % 8] * 2)  # row, column
                f.write(self._pack_bin(pix))

    def get_pixels(self):
        """
        Returns a list containing 64 smaller lists of [R,G,B] pixels
        representing what is currently displayed on the LED matrix
        """

        pixel_list = []
        with open(self._fb_device, 'rb') as f:
            map = self._pix_map[self._rotation]
            for row in range(8):
                for col in range(8):
                    # Two bytes per pixel in fb memory, 16 bit RGB565
                    f.seek(map[row][col] * 2)  # row, column
                    pixel_list.append(self._unpack_bin(f.read(2)))
        return pixel_list

    def set_pixel(self, x, y, *args):
        """
        Updates the single [R,G,B] pixel specified by x and y on the LED matrix
        Top left = 0,0 Bottom right = 7,7

        e.g. ap.set_pixel(x, y, r, g, b)
        or
        pixel = (r, g, b)
        ap.set_pixel(x, y, pixel)
        """

        pixel_error = 'Pixel arguments must be given as (r, g, b) or r, g, b'

        if len(args) == 1:
            pixel = args[0]
            if len(pixel) != 3:
                raise ValueError(pixel_error)
        elif len(args) == 3:
            pixel = args
        else:
            raise ValueError(pixel_error)

        if x > 7 or x < 0:
            raise ValueError('X position must be between 0 and 7')

        if y > 7 or y < 0:
            raise ValueError('Y position must be between 0 and 7')

        for element in pixel:
            if element > 255 or element < 0:
                raise ValueError('Pixel elements must be between 0 and 255')

        with open(self._fb_device, 'wb') as f:
            map = self._pix_map[self._rotation]
            # Two bytes per pixel in fb memory, 16 bit RGB565
            f.seek(map[y][x] * 2)  # row, column
            f.write(self._pack_bin(pixel))

    def get_pixel(self, x, y):
        """
        Returns a list of [R,G,B] representing the pixel specified by x and y
        on the LED matrix. Top left = 0,0 Bottom right = 7,7
        """

        if x > 7 or x < 0:
            raise ValueError('X position must be between 0 and 7')

        if y > 7 or y < 0:
            raise ValueError('Y position must be between 0 and 7')

        pix = None

        with open(self._fb_device, 'rb') as f:
            map = self._pix_map[self._rotation]
            # Two bytes per pixel in fb memory, 16 bit RGB565
            f.seek(map[y][x] * 2)  # row, column
            pix = self._unpack_bin(f.read(2))

        return pix

    def load_image(self, file_path, redraw=True):
        """
        Accepts a path to an 8 x 8 image file and updates the LED matrix with
        the image
        """

        if not os.path.exists(file_path):
            raise IOError('%s not found' % file_path)

        img = Image.open(file_path).convert('RGB')
        pixel_list = list(map(list, img.getdata()))

        if redraw:
            self.set_pixels(pixel_list)

        return pixel_list

    def clear(self, *args):
        """
        Clears the LED matrix with a single colour, default is black / off

        e.g. ap.clear()
        or
        ap.clear(r, g, b)
        or
        colour = (r, g, b)
        ap.clear(colour)
        """

        black = (0, 0, 0)  # default

        if len(args) == 0:
            colour = black
        elif len(args) == 1:
            colour = args[0]
        elif len(args) == 3:
            colour = args
        else:
            raise ValueError('Pixel arguments must be given as (r, g, b) or r, g, b')

        self.set_pixels([colour] * 64)

    def _get_char_pixels(self, s):
        """
        Internal. Safeguards the character indexed dictionary for the
        show_message function below
        """

        if len(s) == 1 and s in self._text_dict.keys():
            return self._text_dict[s]
        else:
            return self._text_dict['?']

    def show_message(
            self,
            text_string,
            scroll_speed=.1,
            text_colour=[255, 255, 255],
            back_colour=[0, 0, 0]
        ):
        """
        Scrolls a string of text across the LED matrix using the specified
        speed and colours
        """

        # We must rotate the pixel map left through 90 degrees when drawing
        # text, see _load_text_assets
        previous_rotation = self._rotation
        self._rotation -= 90
        if self._rotation < 0:
            self._rotation = 270
        string_padding = [back_colour] * 64
        letter_padding = [back_colour] * 8
        # Build pixels from dictionary
        scroll_pixels = []
        scroll_pixels.extend(string_padding)
        for s in text_string:
            scroll_pixels.extend(self._trim_whitespace(self._get_char_pixels(s)))
            scroll_pixels.extend(letter_padding)
        scroll_pixels.extend(string_padding)
        # Recolour pixels as necessary
        coloured_pixels = [
            text_colour if pixel == [255, 255, 255] else back_colour
            for pixel in scroll_pixels
        ]
        # Shift right by 8 pixels per frame to scroll
        scroll_length = len(coloured_pixels) // 8
        for i in range(scroll_length - 8):
            start = i * 8
            end = start + 64
            self.set_pixels(coloured_pixels[start:end])
            time.sleep(scroll_speed)
        self._rotation = previous_rotation

    def show_letter(
            self,
            s,
            text_colour=[255, 255, 255],
            back_colour=[0, 0, 0]
        ):
        """
        Displays a single text character on the LED matrix using the specified
        colours
        """

        if len(s) > 1:
            raise ValueError('Only one character may be passed into this method')
        # We must rotate the pixel map left through 90 degrees when drawing
        # text, see _load_text_assets
        previous_rotation = self._rotation
        self._rotation -= 90
        if self._rotation < 0:
            self._rotation = 270
        pixel_list = [back_colour] * 8
        pixel_list.extend(self._get_char_pixels(s))
        pixel_list.extend([back_colour] * 16)
        coloured_pixels = [
            text_colour if pixel == [255, 255, 255] else back_colour
            for pixel in pixel_list
        ]
        self.set_pixels(coloured_pixels)
        self._rotation = previous_rotation

    ####
    # Environmental sensors
    ####

    def _init_humidity(self):
        """
        Internal. Initialises the humidity sensor via RTIMU
        """

        if not self._humidity_init:
            try:
                self._humidity_init = self._humidity.humidityInit()
                assert(self._humidity_init)
                print("Humidity sensor Init Succeeded")
            except AssertionError:
                raise OSError("Humidity Init Failed, please run as root / use sudo")

    def _init_pressure(self):
        """
        Internal. Initialises the pressure sensor via RTIMU
        """

        if not self._pressure_init:
            try:
                self._pressure_init = self._pressure.pressureInit()
                assert(self._pressure_init)
                print("Pressure sensor Init Succeeded")
            except AssertionError:
                raise OSError("Pressure Init Failed, please run as root / use sudo")

    def get_humidity(self):
        """
        Returns the percentage of relative humidity
        """

        self._init_humidity()  # Ensure humidity sensor is initialised
        humidity = 0
        data = self._humidity.humidityRead()
        if (data[0]):  # Humidity valid
            humidity = data[1]
        return humidity

    def get_temperature_from_humidity(self):
        """
        Returns the temperature in Celsius from the humidity sensor
        """

        self._init_humidity()  # Ensure humidity sensor is initialised
        temp = 0
        data = self._humidity.humidityRead()
        if (data[2]):  # Temp valid
            temp = data[3]
        return temp

    def get_temperature_from_pressure(self):
        """
        Returns the temperature in Celsius from the pressure sensor
        """

        self._init_pressure()  # Ensure pressure sensor is initialised
        temp = 0
        data = self._pressure.pressureRead()
        if (data[2]):  # Temp valid
            temp = data[3]
        return temp

    def get_temperature(self):
        """
        Returns the temperature in Celsius
        """

        return self.get_temperature_from_humidity()

    def get_pressure(self):
        """
        Returns the pressure in Millibars
        """

        self._init_pressure()  # Ensure pressure sensor is initialised
        pressure = 0
        data = self._pressure.pressureRead()
        if (data[0]):  # Pressure valid
            pressure = data[1]
        return pressure

    ####
    # IMU Sensor
    ####

    def _init_imu(self):
        """
        Internal. Initialises the IMU sensor via RTIMU
        """

        if not self._imu_init:
            try:
                self._imu_init = self._imu.IMUInit()
                assert(self._imu_init)
                print("IMU Init Succeeded")
                self._imu_poll_interval = self._imu.IMUGetPollInterval() * 0.001
                # Enable everything on IMU
                self.set_imu_config(True, True, True)
            except AssertionError:
                raise OSError("IMU Init Failed, please run as root / use sudo")

    def set_imu_config(self, compass_enabled, gyro_enabled, accel_enabled):
        """
        Enables and disables the gyroscope, accelerometer and/or magnetometer
        input to the orientation functions
        """

        # If the consuming code always calls this just before reading the IMU
        # the IMU consistently fails to read. So prevent unnecessary calls to
        # IMU config functions using state variables

        self._init_imu()  # Ensure imu is initialised

        if (not isinstance(compass_enabled, bool)
        or not isinstance(gyro_enabled, bool)
        or not isinstance(accel_enabled, bool)):
            raise TypeError('All set_imu_config parameters must be of boolan type')

        if self._compass_enabled != compass_enabled:
            self._compass_enabled = compass_enabled
            self._imu.setCompassEnable(self._compass_enabled)

        if self._gyro_enabled != gyro_enabled:
            self._gyro_enabled = gyro_enabled
            self._imu.setGyroEnable(self._gyro_enabled)

        if self._accel_enabled != accel_enabled:
            self._accel_enabled = accel_enabled
            self._imu.setAccelEnable(self._accel_enabled)

    def _read_imu(self):
        """
        Internal. Tries to read the IMU sensor three times before giving up
        """

        self._init_imu()  # Ensure imu is initialised

        attempts = 0
        success = False

        while not success and attempts < 3:
            success = self._imu.IMURead()
            attempts += 1
            time.sleep(self._imu_poll_interval)

        return success

    def _get_raw_data(self, is_valid_key, data_key):
        """
        Internal. Returns the specified raw data from the IMU when valid
        """

        result = None

        if self._read_imu():
            data = self._imu.getIMUData()
            if data[is_valid_key]:
                raw = data[data_key]
                result = {
                    'x': raw[0],
                    'y': raw[1],
                    'z': raw[2]
                }

        return result

    def get_orientation_radians(self):
        """
        Returns a dictionary object to represent the current orientation in
        radians using the aircraft principal axes of pitch, roll and yaw
        """

        raw = self._get_raw_data('fusionPoseValid', 'fusionPose')

        if raw is not None:
            raw['roll'] = raw.pop('x')
            raw['pitch'] = raw.pop('y')
            raw['yaw'] = raw.pop('z')
            self._last_orientation = raw

        return self._last_orientation

    def get_orientation_degrees(self):
        """
        Returns a dictionary object to represent the current orientation
        in degrees, 0 to 360, using the aircraft principal axes of
        pitch, roll and yaw
        """

        orientation = self.get_orientation_radians()
        for key, val in orientation.items():
            deg = math.degrees(val)  # Result is -180 to +180
            orientation[key] = deg + 360 if deg < 0 else deg
        return orientation

    def get_orientation(self):
        return self.get_orientation_degrees()

    def get_compass(self):
        """
        Gets the direction of North from the magnetometer in degrees
        """

        self.set_imu_config(True, False, False)
        orientation = self.get_orientation_degrees()
        if type(orientation) is dict and 'yaw' in orientation.keys():
            return orientation['yaw']
        else:
            return None

    def get_compass_raw(self):
        """
        Magnetometer x y z raw data in uT (micro teslas)
        """

        raw = self._get_raw_data('compassValid', 'compass')

        if raw is not None:
            self._last_compass_raw = raw

        return self._last_compass_raw

    def get_gyroscope(self):
        """
        Gets the orientation in degrees from the gyroscope only
        """

        self.set_imu_config(False, True, False)
        return self.get_orientation_degrees()

    def get_gyroscope_raw(self):
        """
        Gyroscope x y z raw data in radians per second
        """

        raw = self._get_raw_data('gyroValid', 'gyro')

        if raw is not None:
            self._last_gyro_raw = raw

        return self._last_gyro_raw

    def get_accelerometer(self):
        """
        Gets the orientation in degrees from the accelerometer only
        """

        self.set_imu_config(False, False, True)
        return self.get_orientation_degrees()

    def get_accelerometer_raw(self):
        """
        Accelerometer x y z raw data in Gs
        """

        raw = self._get_raw_data('accelValid', 'accel')

        if raw is not None:
            self._last_accel_raw = raw

        return self._last_accel_raw

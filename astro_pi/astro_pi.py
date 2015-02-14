#!/usr/bin/python
import struct, os, sys, math, time, numpy as np, RTIMU
from PIL import Image # PIL and RTIMU are currently only Python 2 

class AstroPi(object):
    def __init__(self, fb_device = '/dev/fb1', imu_settings_file = 'RTIMULib', text_assets = 'astro_pi_text'):
        self.fb_device = fb_device

        # 0 is With B+ HDMI port facing downwards
        pix_map0 = np.array([
            [ 7,  6,  5,  4,  3,  2,  1,  0],
            [15, 14, 13, 12, 11, 10,  9,  8],
            [23, 22, 21, 20, 19, 18, 17, 16],
            [31, 30, 29, 28, 27, 26, 25, 24], 
            [39, 38, 37, 36, 35, 34, 33, 32],
            [47, 46, 45, 44, 43, 42, 41, 40], 
            [55, 54, 53, 52, 51, 50, 49, 48],
            [63, 62, 61, 60, 59, 58, 57, 56]
        ], int)

        pix_map90 = np.rot90(pix_map0)
        pix_map180 = np.rot90(pix_map90)
        pix_map270 = np.rot90(pix_map180)

        self.pix_map = {
              0: pix_map0,
             90: pix_map90,
            180: pix_map180,
            270: pix_map270 
        }

        self._rotation = 0

        # Load text assets
        dir_path = os.path.dirname(__file__)
        text_image_file = os.path.join(dir_path, '%s.png' % text_assets)
        text_file = os.path.join(dir_path, '%s.txt' % text_assets)

        text_pixels = self.load_image(text_image_file, False)
        with open(text_file, 'r') as f:
            loaded_text = f.read()
        self._text_dict = {}
        for index, s in enumerate(loaded_text):
            start = index * 40
            end = start + 40
            self._text_dict[s] = text_pixels[start:end]

        # Load IMU settings and calibration data
        self.imu_settings = RTIMU.Settings(imu_settings_file)
        self.imu = RTIMU.RTIMU(self.imu_settings)

        try: 
            assert(self.imu.IMUInit())
            print("IMU Init Succeeded");
        except AssertionError:
            raise OSError("IMU Init Failed, please run as root / use sudo");

        self._last_orientation = { 'pitch': 0, 'roll': 0, 'yaw': 0 }
        self._compass_enabled = self._gyro_enabled = self._accel_enabled = False
        self.imu_poll_interval = self.imu.IMUGetPollInterval() * 0.001
        self.set_imu_config(True, True, True) # Enable everything on IMU

    ####
    # LED Matrix
    ####

    def set_rotation(self, r = 0, redraw = True):
        if r in self.pix_map.keys():
            if redraw:
                pixel_list = self.get_pixels()
            self._rotation = r
            if redraw:
                self.set_pixels(pixel_list)
        else:
            raise ValueError('Rotation must be 0, 90, 180 or 270 degrees')

    def pack_bin(self, pix): # Encodes python list [R,G,B] into 16 bit RGB565
        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        bits16 = (r << 11) + (g << 5) + b
        return struct.pack('H', bits16)

    def unpack_bin(self, packed): # Decodes 16 bit RGB565 into python list [R,G,B]
        output = struct.unpack('H', packed)
        bits16 = output[0]
        r = (bits16 & 0xF800) >> 11
        g = (bits16 & 0x7E0) >> 5
        b = (bits16 & 0x1F)
        return [int(r << 3), int(g << 2), int(b << 3)]

    def flip_h(self, redraw = True): # Flip horizontal
        pixel_list = self.get_pixels()
        flipped = []
        for i in range(8):
            offset = i * 8
            flipped.extend(reversed(pixel_list[offset:offset + 8]))
        if redraw:
            self.set_pixels(flipped)
        return flipped

    def flip_v(self, redraw = True): # Flip vertical
        pixel_list = self.get_pixels()
        flipped = []
        for i in reversed(range(8)):
            offset = i * 8
            flipped.extend(pixel_list[offset:offset + 8])
        if redraw:
            self.set_pixels(flipped)
        return flipped

    def set_pixels(self, pixel_list):
        if len(pixel_list) != 64:
            raise ValueError('Pixel lists must have 64 elements')

        for index, pix in enumerate(pixel_list):
            if len(pix) != 3:
                raise ValueError('Pixel at index %d is invalid. Pixels must contain 3 elements: Red, Green and Blue' % index)

            for element in pix:
                if element > 255 or element < 0:
                    raise ValueError('Pixel at index %d is invalid. Pixel elements must be between 0 and 255' % index)

        with open(self.fb_device, 'wb') as f:
            map = self.pix_map[self._rotation]
            for index, pix in enumerate(pixel_list):
                f.seek(map[index // 8][index % 8] * 2) # Two bytes per pixel in fb memory, 16 bit RGB565
                f.write(self.pack_bin(pix))

    def get_pixels(self):
        pixel_list = []
        with open(self.fb_device, 'rb') as f:
            map = self.pix_map[self._rotation]
            for row in range(8):
                for col in range(8):
                    f.seek(map[row][col] * 2) # Two bytes per pixel in fb memory, 16 bit RGB565
                    pixel_list.append(self.unpack_bin(f.read(2)))
        return pixel_list

    def set_pixel_xy(self, x, y, pix):
        if x > 7 or x < 0:
            raise ValueError('X position must be between 0 and 7')

        if y > 7 or y < 0:
            raise ValueError('Y position must be between 0 and 7')

        if len(pix) != 3:
            raise ValueError('Pixels must contain 3 elements: Red, Green and Blue')

        for element in pix:
            if element > 255 or element < 0:
                raise ValueError('Pixel elements must be between 0 and 255')

        with open(self.fb_device, 'wb') as f:
            map = self.pix_map[self._rotation]
            f.seek(map[x][y] * 2) # Two bytes per pixel in fb memory, 16 bit RGB565
            f.write(self.pack_bin(pix))

    def get_pixel_xy(self, x, y):
        if x > 7 or x < 0:
            raise ValueError('X position must be between 0 and 7')

        if y > 7 or y < 0:
            raise ValueError('Y position must be between 0 and 7')

        pix = None

        with open(self.fb_device, 'rb') as f:
            map = self.pix_map[self._rotation]
            f.seek(map[x][y] * 2) # Two bytes per pixel in fb memory, 16 bit RGB565
            pix = self.unpack_bin(f.read(2))

        return pix

    def load_image(self, file_name, redraw = True):
        if not os.path.exists(file_name):
            raise IOError('%s not found' % file_name)

        img = Image.open(file_name).convert('RGB')
        pixel_list = map(list,img.getdata())

        if redraw:
            self.set_pixels(pixel_list)

        return pixel_list

    def clear(self, colour = [0,0,0]):
        self.set_pixels([colour] * 64)

    def get_char_pixels(self, s):
        if len(s) == 1 and s in self._text_dict.keys():
            return self._text_dict[s]
        else:
            return self._text_dict['?']

    def show_message(self, text_string, scroll_speed = .07, text_colour = [255, 255, 255], back_colour = [0, 0, 0]):
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
            scroll_pixels.extend(self.get_char_pixels(s))
            scroll_pixels.extend(letter_padding)
        scroll_pixels.extend(string_padding)
        # Recolour pixels as necessary
        coloured_pixels = [text_colour if pixel == [255,255,255] else back_colour for pixel in scroll_pixels]
        # Shift right by 8 pixels per frame to scroll
        scroll_length = len(coloured_pixels) // 8
        for i in range(scroll_length - 8):
            start = i * 8
            end = start + 64
            self.set_pixels(coloured_pixels[start:end])
            time.sleep(scroll_speed)
        self._rotation = previous_rotation

    def show_letter(self, s, text_colour = [255, 255, 255], back_colour = [0, 0, 0]):
        if len(s) > 1:
            raise ValueError('Only one character may be passed into this method')
        previous_rotation = self._rotation
        self._rotation -= 90
        if self._rotation < 0:
            self._rotation = 270
        pixel_list = [back_colour] * 8
        pixel_list.extend(self.get_char_pixels(s))
        pixel_list.extend([back_colour] * 16)
        coloured_pixels = [text_colour if pixel == [255, 255, 255] else back_colour for pixel in pixel_list]
        self.set_pixels(coloured_pixels)
        self._rotation = previous_rotation

    ####
    # Environmental sensors
    ####

    def get_humidity(self):
        raise NotImplementedError

    def get_temperature(self):
        raise NotImplementedError

    def get_pressure(self):
        raise NotImplementedError

    ####
    # IMU Sensor
    ####

    def set_imu_config(self, compass_enabled, gyro_enabled, accel_enabled):
        # If the consuming code always calls this just before get_orientation the IMU consistently fails to read
        # So prevent unnecessary calls to IMU config functions using state variables

        if not isinstance(compass_enabled, bool) or not isinstance(gyro_enabled, bool) or not isinstance(accel_enabled, bool):
            raise TypeError('All set_imu_config parameters must be of boolan type')

        if self._compass_enabled != compass_enabled:
            self._compass_enabled = compass_enabled
            self.imu.setCompassEnable(self._compass_enabled)

        if self._gyro_enabled != gyro_enabled:
            self._gyro_enabled = gyro_enabled
            self.imu.setGyroEnable(self._gyro_enabled)

        if self._accel_enabled != accel_enabled:
            self._accel_enabled = accel_enabled
            self.imu.setAccelEnable(self._accel_enabled)

    def get_orientation(self): # Consuming code to use directly to combine multiple IMU sensors
        attempts = 0
        success = False

        while not success and attempts < 3:
            success = self.imu.IMURead()
            attempts += 1
            time.sleep(self.imu_poll_interval)

        if success:
            data = self.imu.getIMUData()
            fusionPose = data["fusionPose"]
            r = math.degrees(fusionPose[0]) # Between -180 and +180
            p = math.degrees(fusionPose[1])
            y = math.degrees(fusionPose[2])
            self._last_orientation = {'roll': r + 180, 'pitch': p + 180, 'yaw': y + 180 } # Beteen 0 and 360 is easier for schools

        return self._last_orientation # Current or previous successful IMU read

    def get_compass(self): # Compass angle only, North
        self.set_imu_config(True, False, False)
        orientation = self.get_orientation()
        if type(orientation) is dict and 'yaw' in orientation.keys():
            return orientation['yaw']
        else:
            return None
   
    def get_gyroscope(self): # Gyroscope orientation only
        self.set_imu_config(False, True, False)
        return self.get_orientation()

    def get_accelerometer(self): # Accelerometer orientation only
        self.set_imu_config(False, False, True)
        return self.get_orientation()

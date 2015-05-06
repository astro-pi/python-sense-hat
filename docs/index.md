# Astro Pi

Python module to control the [Astro Pi](http://astro-pi.org/) HAT also known as the Raspberry Pi Sense HAT.

It is highly advised that code written for the Astro Pi [secondary school competition](http://astro-pi.org/secondary-school-competition/) uses this module in Python. This helps guarantee that it will work when we evaluate your code.

## Installation

Have your Pi connected to the Internet and then run the following command (from the command prompt or a Terminal window) to download and start the Astro Pi install script.

```bash
wget -O - http://www.raspberrypi.org/files/astro-pi/astro-pi-install.sh --no-check-certificate | bash
```

This will take about 5 minutes on a Pi 2 and about 15 to 20 minutes on a Pi 1.
When it's finished you'll see the following message:

```
You must reboot to complete the Astro Pi installation
Type:
sudo reboot
and press Enter when ready
```

Reboot the Pi to complete the install:

```bash
sudo reboot
```

The rainbow pattern on the LED matrix should now turn off during boot up.

## Usage

```python
from astro_pi import AstroPi

ap = AstroPi()
```

### LED Matrix

#### set_rotation

If you're using the Pi upside down or sideways you can use this function to correct the orientation of the image being shown.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`r` | Integer | `0` `90` `180` `270` | The angle to rotate the LED matrix though. `0` is with the Raspberry Pi HDMI port facing downwards.
`redraw` | Boolean | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix. Defaults to `True`

Returned type | Explanation
--- | ---
None |

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.set_rotation(180)
```
- - -
#### flip_h

Flips the image on the LED matrix horizontally.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`redraw` | Boolean | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix. Defaults to `True`

Returned type | Explanation
--- | ---
List | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue) representing the flipped image.

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.flip_h()
```
- - -
#### flip_v

Flips the image on the LED matrix vertically.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`redraw` | Boolean | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix when flipped. Defaults to `True`

Returned type | Explanation
--- | ---
List | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue) representing the flipped image.

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.flip_v()
```
- - -
#### set_pixels

Updates the entire LED matrix based on a 64 length list of pixel values.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`pixel_list` | List | `[[R, G, B] * 64]` | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue). Each R-G-B element must be an integer between 0 and 255.

Returned type | Explanation
--- | ---
None |

```python
from astro_pi import AstroPi

ap = AstroPi()

X = [255, 0, 0]  # Red
O = [255, 255, 255]  # White

question_mark = [
O, O, O, X, X, O, O, O,
O, O, X, O, O, X, O, O,
O, O, O, O, O, X, O, O,
O, O, O, O, X, O, O, O,
O, O, O, X, O, O, O, O,
O, O, O, X, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, X, O, O, O, O
]

ap.set_pixels(question_mark)
```
- - -
#### get_pixels

Returned type | Explanation
--- | ---
List | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue) representing the currently displayed image.

```python
from astro_pi import AstroPi

ap = AstroPi()
pixel_list = ap.get_pixels()
```

Note: You will notice that the pixel values you pass into `set_pixels` sometimes change when you read them back with  `get_pixels`. This is because we specify each pixel element as 8 bit numbers (0 to 255) but when they're passed into the Linux frame buffer for the LED matrix the numbers are bit shifted down to fit into RGB 565. 5 bits for red, 6 bits for green and 5 bits for blue. The loss of binary precision when performing this conversion (3 bits lost for red, 2 for green and 3 for blue) accounts for the discrepancies you see.

The `get_pixels` function provides a correct representation of how the pixels end up in frame buffer memory after you've called `set_pixels`.
- - -
#### set_pixel

Sets an individual LED matrix pixel at the specified X-Y coordinate to the specified colour.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`x` | Integer | `0 - 7` | 0 is on the left, 7 on the right.
`y` | Integer |  `0 - 7` | 0 is at the top, 7 at the bottom.
Colour can either be passed as an RGB tuple: |||
`pixel` | Tuple or List |  `(r, g, b)` | Each element must be an integer between 0 and 255.
Or three separate values for red, green and blue: |||
`r` | Integer |  `0 - 255` | The Red element of the pixel.
`g` | Integer |  `0 - 255` | The Green element of the pixel.
`b` | Integer |  `0 - 255` | The Blue element of the pixel.

Returned type | Explanation
--- | ---
None |

```python
from astro_pi import AstroPi

ap = AstroPi()

# examples using (x, y, r, g, b)
ap.set_pixel(0, 0, 255, 0, 0)
ap.set_pixel(0, 7, 0, 255, 0)
ap.set_pixel(7, 0, 0, 0, 255)
ap.set_pixel(7, 7, 255, 0, 255)

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# examples using (x, y, pixel)
ap.set_pixel(0, 0, red)
ap.set_pixel(0, 0, green)
ap.set_pixel(0, 0, blue)
```
- - -
#### get_pixel

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`x` | Integer |  `0 - 7` | 0 is on the left, 7 on the right.
`y` | Integer |  `0 - 7` | 0 is at the top, 7 at the bottom.

Returned type | Explanation
--- | ---
List | Returns a list of `[R, G, B]` representing the colour of an individual LED matrix pixel at the specified X-Y coordinate.

```python
from astro_pi import AstroPi

ap = AstroPi()
top_left_pixel = ap.get_pixel(0, 0)
```

Note: Please read the note under `get_pixels`
- - -
#### load_image

Loads an image file, converts it to RGB format and displays it on the LED matrix. The image must be 8 x 8 pixels in size.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`file_path` | String | Any valid file path. | The file system path to the image file to load.
`redraw` | Boolean | `True` `False` | Whether or not to redraw the loaded image file on the LED matrix. Defaults to `True`

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.load_image("space_invader.png")
```

Returned type | Explanation
--- | ---
List | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue) representing the loaded image after RGB conversion.

```python
from astro_pi import AstroPi

ap = AstroPi()
invader_pixels = ap.load_image("space_invader.png", redraw=False)
```
- - -
#### clear

Sets the entire LED matrix to a single colour, defaults to blank / off.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`colour` | Tuple or List | `(r, g, b)` | A tuple or list containing the RGB (red, green, blue) values of the colour. Each element must be an integer between 0 and 255. Defaults to `(0, 0, 0)`.
Alternatively, the RGB values can be passed individually:|||
`r` | Integer |  `0 - 255` | The Red element of the colour.
`g` | Integer |  `0 - 255` | The Green element of the colour.
`b` | Integer |  `0 - 255` | The Blue element of the colour.

```python
from astro_pi import AstroPi
from time import sleep

ap = AstroPi()

red = (255, 0, 0)

ap.clear()  # no arguments defaults to off
sleep(1)
ap.clear(red)  # passing in an RGB tuple
sleep(1)
ap.clear(255, 255, 255)  # passing in r, g and b values of a colour
```
- - -
#### show_message

Scrolls a text message from right to left across the LED matrix and at the specified speed, in the specified colour and background colour.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`text_string` | String | Any text string. | The message to scroll.
`scroll_speed` | Float | Any floating point number. | The speed at which the text should scroll. This value represents the time paused for between shifting the text to the left by one column of pixels. Defaults to `0.1`
`text_colour` | List | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the text. Each R-G-B element must be an integer between 0 and 255. Defaults to `[255, 255, 255]` white.
`back_colour` | List | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the background. Each R-G-B element must be an integer between 0 and 255. Defaults to `[0, 0, 0]` black / off.

Returned type | Explanation
--- | ---
None |

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.show_message("One small step for Pi!", text_colour=[255, 0, 0])
```
- - -
#### show_letter

Displays a single text character on the LED matrix.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`s` | String | A text string of length 1. | The letter to show.
`text_colour` | List | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the letter. Each R-G-B element must be an integer between 0 and 255. Defaults to `[255, 255, 255]` white.
`back_colour` | List | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the background. Each R-G-B element must be an integer between 0 and 255. Defaults to `[0, 0, 0]` black / off.

Returned type | Explanation
--- | ---
None |

```python
import time
from astro_pi import AstroPi

ap = AstroPi()

for i in reversed(range(0,10)):
    ap.show_letter(str(i))
    time.sleep(1)
```
- - -
### Environmental sensors

#### get_humidity

Gets the percentage of relative humidity from the humidity sensor.

Returned type | Explanation
--- | ---
Float | The percentage of relative humidity.

```python
from astro_pi import AstroPi

ap = AstroPi()
humidity = ap.get_humidity()
print("Humidity: %s %%rH" % humidity)
```
- - -
#### get_temperature

Calls `get_temperature_from_humidity` below.

```python
from astro_pi import AstroPi

ap = AstroPi()
temp = ap.get_temperature()
print("Temperature: %s C" % temp)
```
- - -
#### get_temperature_from_humidity

Gets the current temperature in degrees Celsius from the humidity sensor.

Returned type | Explanation
--- | ---
Float | The current temperature in degrees Celsius.

```python
from astro_pi import AstroPi

ap = AstroPi()
temp = ap.get_temperature_from_humidity()
print("Temperature: %s C" % temp)
```
- - -
#### get_temperature_from_pressure

Gets the current temperature in degrees Celsius from the pressure sensor.

Returned type | Explanation
--- | ---
Float | The current temperature in degrees Celsius.

```python
from astro_pi import AstroPi

ap = AstroPi()
temp = ap.get_temperature_from_pressure()
print("Temperature: %s C" % temp)
```
- - -
#### get_pressure

Gets the current pressure in Millibars from the pressure sensor.

Returned type | Explanation
--- | ---
Float | The current pressure in Millibars.

```python
from astro_pi import AstroPi

ap = AstroPi()
pressure = ap.get_pressure()
print("Pressure: %s Millibars" % pressure)
```
- - -
### IMU Sensor

The IMU (inertial measurement unit) sensor is a combination of three sensors, each with an x, y and z axis. For this reason it's considered be a 9 dof (degrees of freedom) sensor.

- Gyroscope
- Accelerometer
- Magnetometer (compass)

This API allows you to use these sensors in any combination to measure orientation or as individual sensors in their own right.

#### set_imu_config

Enables and disables the gyroscope, accelerometer and/or magnetometer contribution to the get orientation functions below.

Parameter | Type | Valid values | Explanation
--- | --- | --- | ---
`compass_enabled` | Boolean | `True` `False` | Whether or not the compass should be enabled.
`gyro_enabled` | Boolean | `True` `False` | Whether or not the gyroscope should be enabled.
`accel_enabled` | Boolean | `True` `False` | Whether or not the accelerometer should be enabled.

Returned type | Explanation
--- | ---
None |

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.set_imu_config(False, True, False)  # gyroscope only
```
- - -
#### get_orientation_radians

Gets the current orientation in radians using the aircraft principal axes of pitch, roll and yaw.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `pitch`, `roll` and `yaw`. The values are Floats representing the angle of the axis in radians.

```python
from astro_pi import AstroPi

ap = AstroPi()
orientation_rad = ap.get_orientation_radians()
print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation_rad))
```
- - -
#### get_orientation_degrees

Gets the current orientation in degrees using the aircraft principal axes of pitch, roll and yaw.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `pitch`, `roll` and `yaw`. The values are Floats representing the angle of the axis in degrees.

```python
from astro_pi import AstroPi

ap = AstroPi()
orientation = ap.get_orientation_degrees()
print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation))
```
- - -
#### get_orientation

Calls `get_orientation_degrees` above.

```python
from astro_pi import AstroPi

ap = AstroPi()
orientation = ap.get_orientation()
print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation))
```
- - -
#### get_compass

Calls `set_imu_config` to disable the gyroscope and accelerometer then gets the direction of North from the magnetometer in degrees.

Returned type | Explanation
--- | ---
Float | The direction of North.

```python
from astro_pi import AstroPi

ap = AstroPi()
north = ap.get_compass()
print("North: %s" % north)
```
- - -
#### get_compass_raw

Gets the raw x, y and z axis magnetometer data.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `x`, `y` and `z`. The values are Floats representing the magnetic intensity of the axis in **teslas**.

```python
from astro_pi import AstroPi

ap = AstroPi()
raw = ap.get_compass_raw()
print("x: {x}, y: {y}, z: {z}".format(**raw))
```
- - -
#### get_gyroscope

Calls `set_imu_config` to disable the magnetometer and accelerometer then gets the current orientation from the gyroscope only.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `pitch`, `roll` and `yaw`. The values are Floats representing the angle of the axis in degrees.

```python
from astro_pi import AstroPi

ap = AstroPi()
gyro_only = ap.get_gyroscope()
print("p: {pitch}, r: {roll}, y: {yaw}".format(**gyro_only))
```
- - -
#### get_gyroscope_raw

Gets the raw x, y and z axis gyroscope data.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `x`, `y` and `z`. The values are Floats representing the rotational intensity of the axis in **radians per second**.

```python
from astro_pi import AstroPi

ap = AstroPi()
raw = ap.get_gyroscope_raw()
print("x: {x}, y: {y}, z: {z}".format(**raw))
```
- - -
#### get_accelerometer

Calls `set_imu_config` to disable the magnetometer and gyroscope then gets the current orientation from the accelerometer only.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `pitch`, `roll` and `yaw`. The values are Floats representing the angle of the axis in degrees.

```python
from astro_pi import AstroPi

ap = AstroPi()
accel_only = ap.get_accelerometer()
print("p: {pitch}, r: {roll}, y: {yaw}".format(**accel_only))
```
- - -
#### get_accelerometer_raw

Gets the raw x, y and z axis accelerometer data.

Returned type | Explanation
--- | ---
Dictionary | A dictionary object indexed by the strings `x`, `y` and `z`. The values are Floats representing the acceleration intensity of the axis in **Gs**.

```python
from astro_pi import AstroPi

ap = AstroPi()
raw = ap.get_accelerometer_raw()
print("x: {x}, y: {y}, z: {z}".format(**raw))
```

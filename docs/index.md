# Astro Pi

Python module to control the [Astro Pi](http://astro-pi.org/) HAT also known as the Raspberry Pi Sense HAT.

It is highly advised that code written for the Astro Pi [secondary school competition](http://astro-pi.org/secondary-school-competition/) uses this module in Python. This helps guarantee that it will work when we evaluate your code.

## Installation

Coming soon.

## Usage

```python
from astro_pi import AstroPi

ap = AstroPi()
```


### LED Matrix

#### set_rotation

If you're using the Pi upside down or sideways you can use this function to correct the orientation of the image being shown.

Parameter | Valid values | Explanation
--- | --- | ---
`r` | `0` `90` `180` `270` | The angle to rotate the LED matrix though. `0` is with the Raspberry Pi HDMI port facing downwards.
`redraw` | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix. Defaults to `True`

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.set_rotation(180)
```

#### flip_h

Flips the image on the LED matrix horizontally.

Parameter | Valid values | Explanation
--- | --- | ---
`redraw` | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix. Defaults to `True`

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.flip_h()
```

#### flip_v

Flips the image on the LED matrix vertically.

Parameter | Valid values | Explanation
--- | --- | ---
`redraw` | `True` `False` | Whether or not to redraw what is already being displayed on the LED matrix. Defaults to `True`

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.flip_v()
```

#### set_pixels

Updates the entire LED matrix based on a 64 length list of pixel values.

Parameter | Valid values | Explanation
--- | --- | ---
`pixel_list` | `[[R, G, B] * 64]` | A list containing 64 smaller lists of `[R, G, B]` pixels (red, green, blue). Each R-G-B element must be an integer between 0 and 255.

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

#### get_pixels

Returns a 64 length list of pixel values representing what is currently displayed on the LED matrix.

The returned list will contain 64 smaller lists of `[R, G, B]` pixels (red, green, blue). Each R-G-B element will be an integer between 0 and 255.

```python
from astro_pi import AstroPi

ap = AstroPi()
pixel_list = ap.get_pixels()
```

Note: You will notice that the pixel values you pass into `set_pixels` sometimes change when you read them back with  `get_pixels`. This is because we specify each pixel element as 8 bit numbers (0 to 255) but when they're passed into the Linux frame buffer for the LED matrix the numbers are bit shifted down to fit into RGB 565. 5 bits for red, 6 bits for green and 5 bits for blue. The loss of binary precision when performing this conversion (3 bits lost for red, 2 for green and 3 for blue) accounts for the discrepancies you see.

The `get_pixels` function provides a correct representation of how the pixels end up in frame buffer memory after you've called `set_pixels`.

#### set_pixel_xy

Sets an individual LED matrix pixel at the specified X-Y coordinate to the specified colour.

Parameter | Valid values | Explanation
--- | --- | ---
`x` | `0 - 7` | 0 is on the left, 7 on the right.
`y` | `0 - 7` | 0 is at the top, 7 at the bottom.
`pix` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour the pixel should be set to. Each R-G-B element must be an integer between 0 and 255.

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.set_pixel_xy(0, 0, [255, 0, 0])
ap.set_pixel_xy(0, 7, [0, 255, 0])
ap.set_pixel_xy(7, 0, [0, 0, 255])
ap.set_pixel_xy(7, 7, [255, 0, 255])
```

#### get_pixel_xy

Returns a list of `[R, G, B]` representing the colour of an individual LED matrix pixel at the specified X-Y coordinate.

Parameter | Valid values | Explanation
--- | --- | ---
`x` | `0 - 7` | 0 is on the left, 7 on the right.
`y` | `0 - 7` | 0 is at the top, 7 at the bottom.

```python
from astro_pi import AstroPi

ap = AstroPi()
top_left_pixel = ap.get_pixel_xy(0, 0)
```

Note: Please read the note under `get_pixels`

#### load_image

Loads an image file, converts it to RGB format and displays it on the LED matrix. The image must be 8 x 8 pixels in size.

Parameter | Valid values | Explanation
--- | --- | ---
`file_path` | `String` | The file system path to the image file to load.
`redraw` | `True` `False` | Whether or not to redraw the loaded image file on the LED matrix. Defaults to `True`

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.load_image("space_invader.png")
```

The function also returns a pixel list representing the image converted into RGB format if further manipulation is desired.

```python
from astro_pi import AstroPi

ap = AstroPi()
invader_pixels = ap.load_image("space_invader.png", redraw=False)
```

#### clear

Sets the entire LED matrix to a single colour, defaults to blank / off.

Parameter | Valid values | Explanation
--- | --- | ---
`colour` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour. Each R-G-B element must be an integer between 0 and 255. Defaults to `[0, 0, 0]`

```python
import time
from astro_pi import AstroPi

ap = AstroPi()
ap.clear([255, 255, 255])
time.sleep(1)
ap.clear()
```

#### show_message

Scrolls a text message from right to left across the LED matrix and at the specified speed, in the specified colour and background colour.

Parameter | Valid values | Explanation
--- | --- | ---
`text_string` | `String` | The message to scroll. 
`scroll_speed` | `Float` | The speed at which the text should scroll. This value represents the time paused for between shifting the text to the left by one column of pixels. Defaults to `0.1`
`text_colour` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the text. Each R-G-B element must be an integer between 0 and 255. Defaults to `[255, 255, 255]` white.
`back_colour` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the background. Each R-G-B element must be an integer between 0 and 255. Defaults to `[0, 0, 0]` black / off.

```python
from astro_pi import AstroPi

ap = AstroPi()
ap.show_message("One small step for Pi!", text_colour=[255, 0, 0])
```

#### show_letter

Displays a single text character on the LED matrix.

Parameter | Valid values | Explanation
--- | --- | ---
`s` | `String` | The letter to show, must be a string of length 1.
`text_colour` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the letter. Each R-G-B element must be an integer between 0 and 255. Defaults to `[255, 255, 255]` white.
`back_colour` | `[R, G, B]` | A list containing the R-G-B (red, green, blue) colour of the background. Each R-G-B element must be an integer between 0 and 255. Defaults to `[0, 0, 0]` black / off.

```python
import time
from astro_pi import AstroPi

ap = AstroPi()

for i in reversed(range(0,10)):
    ap.show_letter(str(i))
    time.sleep(1)
```

### Environmental sensors

#### get_humidity

Gets the percentage of relative humidity, the value returned will be a Float.

```python
from astro_pi import AstroPi

ap = AstroPi()
humidity = ap.get_humidity()
```

### IMU Sensor

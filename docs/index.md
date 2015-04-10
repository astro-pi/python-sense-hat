# Astro Pi

Python module to control the [Astro Pi](http://astro-pi.org/) HAT also known as the Raspberry Pi Sense HAT.

It is highly advised that code written for the Astro Pi [secondary school competition](http://astro-pi.org/secondary-school-competition/) uses this module in Python. This helps guarantee that it will work when we evaluate your code.

## Installation

Coming soon.

## Usage

```python
#!/usr/bin/python
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
#!/usr/bin/python
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
#!/usr/bin/python
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
#!/usr/bin/python
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
#!/usr/bin/python
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

### Environmental sensors

### IMU Sensor

# Sense HAT

Python module to control the [Raspberry Pi Sense HAT](https://www.raspberrypi.com/products/sense-hat/)

## Features

The Sense HAT features an 8x8 RGB LED matrix, a mini joystick and the following sensors:

- Gyroscope
- Accelerometer
- Magnetometer
- Temperature
- Humidity
- Barometric pressure
- Light and colour

## Install

Install the Sense HAT software by opening a Terminal window and entering the following commands (while connected to the Internet):

```bash
sudo apt-get update
sudo apt-get install sense-hat
sudo reboot
```

## Usage

Hello world example:

```python
from sense_hat import SenseHat

sense = SenseHat()

sense.show_message("Hello world!")
```

See the [API reference](api.md) for full documentation of the library's functions. See [examples](examples/README.md).

## Development

This library is maintained by the Raspberry Pi Foundation on GitHub at [github.com/astro-pi/python-sense-hat](https://github.com/astro-pi/python-sense-hat)

See the [changelog](changelog.md).

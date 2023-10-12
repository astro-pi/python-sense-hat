#Sense HAT

Python module to control the `Raspberry Pi` Sense HAT used in the `Astro Pi` mission - an education outreach programme for UK schools sending code experiments to the International Space Station.

Hardware
========

The Sense HAT features an 8x8 RGB LED matrix, a mini joystick and the following sensors:

* Gyroscope
* Accelerometer
* Magnetometer
* Temperature
* Humidity
* Barometric pressure

Buy
===

Buy the Sense HAT from:

* `The Pi Hut`
* `Pimoroni`
* `Amazon (UK)`
* `element14`
* `adafruit`
* `Amazon (USA)`


Installation
============

To install the Sense HAT software, enter the following commands in a terminal::

    sudo apt-get update
    sudo apt-get install sense-hat
    sudo reboot

Usage
=====

Import the sense_hat module and instantiate a SenseHat object::

    from sense_hat import SenseHat

    sense = SenseHat()

Documentation
=============

Comprehensive documentation is available at `https://sense-hat.readthedocs.io/en/latest/`.

Contributors
============

* `Dave Honess`
* `Ben Nuttall`
* `Serge Schneider`
* `Dave Jones`
* `Tyler Laws`
* `George Boukeas`

Open Source
===========

* The code is licensed under the `BSD Licence`
* The project source code is hosted on `GitHub`
* Please use `GitHub issues` to submit bugs and report issues

URLs
=====

* Raspberry Pi: https://www.raspberrypi.org/
* Astro Pi: http://www.astro-pi.org/
* sense-hat.readthedocs.io: https://sense-hat.readthedocs.io/en/latest/
* Dave Honess: https://github.com/davidhoness
* Ben Nuttall: https://github.com/bennuttall
* Serge Schneider: https://github.com/XECDesign
* Dave Jones: https://github.com/waveform80
* Tyler Laws: https://github.com/tyler-laws
* George Boukeas: https://github.com/boukeas
* BSD Licence: http://opensource.org/licenses/BSD-3-Clause
* GitHub: https://github.com/astro-pi/python-sense-hat
* GitHub Issues: https://github.com/astro-pi/python-sense-hat/issues
* `The Pi Hut`: http://thepihut.com/products/raspberry-pi-sense-hat-astro-pi
* `Pimoroni`: https://shop.pimoroni.com/products/raspberry-pi-sense-hat
* `Amazon (UK)`: http://www.amazon.co.uk/Raspberry-Pi-2483095-Sense-HAT/dp/B014T2IHQ8/
* element14: https://www.element14.com/community/docs/DOC-78155/l/raspberry-pi-sense-hat
* adafruit: https://www.adafruit.com/products/2738
* Amazon (USA): http://www.amazon.com/Raspberry-Pi-Sense-HAT-AstroPi/dp/B014HDG74S

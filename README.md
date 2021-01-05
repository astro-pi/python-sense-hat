=========
Sense HAT
=========

Python module to control the `Raspberry Pi`_ Sense HAT used in the `Astro Pi`_ mission - an education outreach programme for UK schools sending code experiments to the International Space Station.

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

* `The Pi Hut`_
* `Pimoroni`_
* `Amazon (UK)`_
* `element14`_
* `adafruit`_
* `Amazon (USA)`_


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

Comprehensive documentation is available at `pythonhosted.org/sense-hat`_

Contributors
============

* `Dave Honess`_
* `Ben Nuttall`_
* `Serge Schneider`_
* `Dave Jones`_
* `Tyler Laws`_

Open Source
===========

* The code is licensed under the `BSD Licence`_
* The project source code is hosted on `GitHub`_
* Please use `GitHub issues`_ to submit bugs and report issues

.. _Raspberry Pi: https://www.raspberrypi.org/
.. _Astro Pi: http://www.astro-pi.org/
.. _pythonhosted.org/sense-hat: http://pythonhosted.org/sense-hat/
.. _Dave Honess: https://github.com/davidhoness
.. _Ben Nuttall: https://github.com/bennuttall
.. _Serge Schneider: https://github.com/XECDesign
.. _Dave Jones: https://github.com/waveform80
.. _Tyler Laws: https://github.com/tyler-laws
.. _BSD Licence: http://opensource.org/licenses/BSD-3-Clause
.. _GitHub: https://github.com/RPi-Distro/python-sense-hat
.. _GitHub Issues: https://github.com/RPi-Distro/python-sense-hat/issues
.. _`The Pi Hut`: http://thepihut.com/products/raspberry-pi-sense-hat-astro-pi
.. _`Pimoroni`: https://shop.pimoroni.com/products/raspberry-pi-sense-hat
.. _`Amazon (UK)`: http://www.amazon.co.uk/Raspberry-Pi-2483095-Sense-HAT/dp/B014T2IHQ8/
.. _element14: https://www.element14.com/community/docs/DOC-78155/l/raspberry-pi-sense-hat
.. _adafruit: https://www.adafruit.com/products/2738
.. _Amazon (USA): http://www.amazon.com/Raspberry-Pi-Sense-HAT-AstroPi/dp/B014HDG74S

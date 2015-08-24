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

Coming soon

Installation
============

To install the Sense HAT software, enter the following commands in a terminal::

    sudo apt-get update
    sudo apt-get install sense-hat
    sudo pip-3.2 install pillow
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
.. _BSD Licence: http://opensource.org/licenses/BSD-3-Clause
.. _GitHub: https://github.com/RPi-Distro/python-sense-hat
.. _GitHub Issues: https://github.com/RPi-Distro/python-sense-hat/issues

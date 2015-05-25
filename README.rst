============
Astro Pi HAT
============

Python module to control the Astro Pi / Sense HAT for the `Raspberry Pi`_ used in the `Astro Pi`_ mission - an education outreach programme for UK schools sending code experiments to the International Space Station.

Installation
============

With your Pi connected to the Internet, run the following command (from the command prompt or a Terminal window) to download and start the Astro Pi install script::

    wget -O - https://www.raspberrypi.org/files/astro-pi/astro-pi-install.sh --no-check-certificate | bash

This will take about 5 minutes on a Pi 2 and about 15 to 20 minutes on a Pi 1. When it's finished you'll see the following message::

    You must reboot to complete the Astro Pi installation
    Type:
    sudo reboot
    and press Enter when ready

Reboot the Pi to complete the install::

    sudo reboot

The rainbow pattern on the LED matrix should now turn off during boot up.

Usage
=====

Import the Astro Pi module and instantiate an object::

    from astro_pi import AstroPi

    ap = AstroPi()

Documentation
=============

Comprehensive documentation is available at `pythonhosted.org/astro-pi`_

Contributors
============

* `Dave Honess`_
* `Ben Nuttall`_

Open Source
===========

* The code is licensed under the `BSD Licence`_
* The project source code is hosted on `GitHub`_
* Please use `GitHub issues`_ to submit bugs and report issues

.. _Raspberry Pi: https://www.raspberrypi.org/
.. _Astro Pi: http://www.astro-pi.org/
.. _pythonhosted.org/astro-pi: http://pythonhosted.org/astro-pi/
.. _Dave Honess: https://github.com/davidhoness
.. _Ben Nuttall: https://github.com/bennuttall
.. _BSD Licence: http://opensource.org/licenses/BSD-3-Clause
.. _GitHub: https://github.com/astro-pi/astro-pi-hat
.. _GitHub Issues: https://github.com/astro-pi/astro-pi-hat/issues

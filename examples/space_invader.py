#!/usr/bin/python
import sys
sys.path.insert(1, '/home/pi/python-sense-hat')
from sense_hat import SenseHat

sense = SenseHat()
sense.clear()
sense.load_image("/home/pi/pi3d_demos/textures/Raspi256x256.png")

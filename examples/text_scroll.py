#!/usr/bin/python
import sys
sys.path.insert(1, '/home/pi/python-sense-hat')
from sense_hat import SenseHat

sense = SenseHat()
sense.set_rotation(180)
red = (255, 0, 0)
sense.show_message("One small step for Pi!", text_colour=red)

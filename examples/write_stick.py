#!/usr/bin/python3
import time
from sense_hat import SenseStick, SenseHat
import sys

"""
    Simple program that writes letters based on joystick.
    
    Uses SenseStick for input.
"""

print("Press Ctrl-C to quit")

sense = SenseHat()
sense.clear((0,50,200))  

stick = SenseStick()

try:
    while True:
        press = stick.read() # (time, code, up/down)
        up_down = press[2]
        key_code = press[1]
        if key_code == stick.KEY_UP:
          sense.show_letter("U", back_colour = (150,150,0))
        elif key_code == stick.KEY_DOWN:
          sense.show_letter("D", back_colour = (150,0,150))
        elif key_code == stick.KEY_RIGHT:
          sense.show_letter("R", back_colour = (0,150,150))
        elif key_code == stick.KEY_LEFT:
          sense.show_letter("L", back_colour = (0,0,0), \
            text_colour = (200,0,0))
        elif key_code == stick.KEY_ENTER:
          sense.show_letter("E", back_colour = (200,200,200), \
            text_colour = (0,0,0))
        
except KeyboardInterrupt:
    pass
sys.exit()


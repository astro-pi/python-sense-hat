#!/usr/bin/python3
import time
from sense_hat import SenseStick, SenseHat
import sys

"""
    An implementation of evdev_joystick.py without evdev.
"""


print("Press Ctrl-C to quit")
time.sleep(1)

sense = SenseHat()
sense.clear()  # Blank the LED matrix

stick = SenseStick()

# 0, 0 = Top left
# 7, 7 = Bottom right
UP_PIXELS = [[3, 0], [4, 0]]
DOWN_PIXELS = [[3, 7], [4, 7]]
LEFT_PIXELS = [[0, 3], [0, 4]]
RIGHT_PIXELS = [[7, 3], [7, 4]]
CENTRE_PIXELS = [[3, 3], [4, 3], [3, 4], [4, 4]]


def set_pixels(pixels, col):
    for p in pixels:
            sense.set_pixel(p[0], p[1], col[0], col[1], col[2])
            
def handle_code(code, colour):
    if code == stick.KEY_DOWN:
        set_pixels(DOWN_PIXELS, colour)
    elif code == stick.KEY_UP:
        set_pixels(UP_PIXELS, colour)
    elif code == stick.KEY_LEFT:
        set_pixels(LEFT_PIXELS, colour)
    elif code == stick.KEY_RIGHT:
        set_pixels(RIGHT_PIXELS, colour)
    elif code == stick.KEY_ENTER:
        set_pixels(CENTRE_PIXELS, colour)

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

going = True

try:
    while going:
        press = stick.read() # (time, code, up/down)
        up_down = press[2]
        key_code = press[1]
        if up_down == 1:  # key down
            handle_code(key_code, WHITE)
        if up_down == 0:  # key up
            handle_code(key_code, BLACK)
#        time.sleep(.001)
except KeyboardInterrupt:
    pass
sys.exit()
        

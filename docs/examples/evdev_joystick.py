#!/usr/bin/python
import sys
import time
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes

print("Press Ctrl-C to quit")
time.sleep(1)

sense = SenseHat()
sense.clear()  # Blank the LED matrix

found = False;
devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    if dev.name == 'Raspberry Pi Sense HAT Joystick':
        found = True;
        break

if not(found):
    print('Raspberry Pi Sense HAT Joystick not found. Aborting ...')
    sys.exit()

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
    if code == ecodes.KEY_DOWN:
        set_pixels(DOWN_PIXELS, colour)
    elif code == ecodes.KEY_UP:
        set_pixels(UP_PIXELS, colour)
    elif code == ecodes.KEY_LEFT:
        set_pixels(LEFT_PIXELS, colour)
    elif code == ecodes.KEY_RIGHT:
        set_pixels(RIGHT_PIXELS, colour)
    elif code == ecodes.KEY_ENTER:
        set_pixels(CENTRE_PIXELS, colour)


BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

try:
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:  # key down
                handle_code(event.code, WHITE)
            if event.value == 0:  # key up
                handle_code(event.code, BLACK)
except KeyboardInterrupt:
    sys.exit()

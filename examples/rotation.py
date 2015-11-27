#!/usr/bin/python
import sys
import time
from sense_hat import SenseHat

X = (255, 0, 0)
O = (255, 255, 255)

question_mark = [
    O, O, O, X, X, O, O, O,
    O, O, X, O, O, X, O, O,
    O, O, O, O, O, X, O, O,
    O, O, O, O, X, O, O, O,
    O, O, O, X, O, O, O, O,
    O, O, O, X, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, X, O, O, O, O
]

sense = SenseHat()

sense.set_pixels(question_mark)

sense.set_pixel(0, 0, 255, 0, 0)
sense.set_pixel(0, 7, 0, 255, 0)
sense.set_pixel(7, 0, 0, 0, 255)
sense.set_pixel(7, 7, 255, 0, 255)

while True:
    for r in [0, 90, 180, 270]:
        sense.set_rotation(r)
        time.sleep(0.3)

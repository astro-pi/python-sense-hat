#!/usr/bin/python
from astro_pi import AstroPi

ap = AstroPi()

r = 255
g = 0
b = 0


def next_colour():
    global r
    global g
    global b

    if (r == 255 and g < 255 and b == 0):
        g += 1

    if (g == 255 and r > 0 and b == 0):
        r -= 1

    if (g == 255 and b < 255 and r == 0):
        b += 1

    if (b == 255 and g > 0 and r == 0):
        g -= 1

    if (b == 255 and r < 255 and g == 0):
        r += 1

    if (r == 255 and b > 0 and g == 0):
        b -= 1

while True:
    ap.clear([r, g, b])
    next_colour()

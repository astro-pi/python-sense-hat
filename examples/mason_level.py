#!/usr/bin/python3
# coding: utf-8

import sys
import time
from sense_hat import SenseHat

def limit(lcd_pos):
    pos_lim = 6
    if lcd_pos < 0:
        return 0
    if lcd_pos > pos_lim:
        return pos_lim
    return lcd_pos

def main():
    sense = SenseHat()
    color = (255, 0, 0)
    prev_x = -1
    prev_y = -1
    while True:
        acc = sense.get_accelerometer_raw()
        x = limit(round(-10 * acc['x'] + 3))
        y = limit(round(-10 * acc['y'] + 3))
        if x != prev_x or y != prev_y:
            sense.clear()
        sense.set_pixel(x, y, *color)
        prev_x = x
        prev_y = y
        time.sleep(0.08)

if __name__ == '__main__':
    main()

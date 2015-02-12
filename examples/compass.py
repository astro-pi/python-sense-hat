#!/usr/bin/python
import astro_pi

edge_loop = [0, 1, 2, 3, 4, 5, 6, 7, 15, 23, 31, 39, 47, 55, 63, 62, 61, 60, 59, 58, 57, 56, 48, 40, 32, 24, 16, 8]

ap = astro_pi.create()
ap.set_rotation(0)
ap.clear()

prev_x = 0
prev_y = 0

while True:
    dir = ap.get_compass()
    edge_index = int((len(edge_loop)/360.0) * dir)
    offset = edge_loop[edge_index]

    y = offset // 8
    x = offset % 8

    if x != prev_x or y != prev_y:
        ap.set_pixel_xy(prev_x, prev_y, [0,0,0])

    ap.set_pixel_xy(x, y, [0,0,255])

    prev_x = x
    prev_y = y

#!/usr/bin/python
import os
import time
import pygame  # See http://www.pygame.org/docs

# Set SDL to use the main Linux frame buffer so it does not need the Desktop
os.environ["SDL_VIDEODRIVER"] = "fbcon"  # Remove this line if using Desktop

print("Press Escape to quit")
time.sleep(1)

from pygame.locals import *
from astro_pi import AstroPi

pygame.init()
pygame.display.set_mode((640, 480))

ap = AstroPi()
ap.clear()  # Blank the LED matrix

# 0, 0 = Top left
# 7, 7 = Bottom right
UP_PIXELS = [[0, 3], [0, 4]]
DOWN_PIXELS = [[7, 3], [7, 4]]
LEFT_PIXELS = [[3, 0], [4, 0]]
RIGHT_PIXELS = [[3, 7], [4, 7]]
CENTRE_PIXELS = [[3, 3], [3, 4], [4, 3], [4, 4]]


def set_pixels(pixels, colour):
    for p in pixels:
        ap.set_pixel_xy(p[0], p[1], colour)


def handle_event(event, colour):
    if event.key == pygame.K_DOWN:
        set_pixels(DOWN_PIXELS, colour)
    elif event.key == pygame.K_UP:
        set_pixels(UP_PIXELS, colour)
    elif event.key == pygame.K_LEFT:
        set_pixels(LEFT_PIXELS, colour)
    elif event.key == pygame.K_RIGHT:
        set_pixels(RIGHT_PIXELS, colour)
    elif event.key == pygame.K_RETURN:
        set_pixels(CENTRE_PIXELS, colour)


running = True

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            handle_event(event, WHITE)
        if event.type == KEYUP:
            handle_event(event, BLACK)

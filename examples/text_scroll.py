#!/usr/bin/python
from astro_pi import AstroPi

ap = AstroPi()
ap.set_rotation(180)
ap.show_message("One small step for Pi!", text_colour=[255, 0, 0])

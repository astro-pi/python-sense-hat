#!/usr/bin/env python
import os
from sense_hat import SenseHat

sense = SenseHat()
sense.clear()
sense.load_image("space_invader.png")

os.system("bash -c \"read -n 1 -s -p 'Press any key to exit...'\"")
sense.clear()

#!/usr/bin/python3
import time
from sense_hat import SenseHat
import curses
import sys

"""
    A bug on a colored background, responding to keypresses.

    Modify the starting state in the `state` dict.
    The background changes colors based on the bug's xy coords.

    This version handles input via the curses stlib module.
"""

state = { "bug_x" : 4,
          "bug_y" : 4,
          "bug_rgb" : (250,250,250) }

sense = SenseHat()

def setscreen():
    """Takes x and y vales and alters screen state"""
    global state
    x = state["bug_x"]
    y = state["bug_y"]
    if sense.low_light:
        zero = 8
    else:
        zero = 48
    brightness = 255 -zero 
    g = int(((x * 32)/255) * brightness + zero)
    b = int(((y * 32)/255) * brightness + zero)
    r = abs(g - b)
    sense.clear((r,g,b))
    print(r,g,b)
    
def draw_bug(char):
    global state
    key_code = char
    if key_code == curses.KEY_ENTER or key_code == 10 or key_code == 13:
        sys.exit()
    elif key_code == curses.KEY_UP:
        state["bug_x"] = state["bug_x"]
        state["bug_y"] = 7 if state["bug_y"] == 0 else state["bug_y"] - 1
        setscreen()
        sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])
    elif key_code == curses.KEY_DOWN:
        state["bug_x"] = state["bug_x"]
        state["bug_y"] = 0 if state["bug_y"] == 7 else state["bug_y"] + 1
        setscreen()
        sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])
    elif key_code == curses.KEY_RIGHT:
        state["bug_x"] = 0 if state["bug_x"] == 7 else state["bug_x"] + 1
        state["bug_y"] = state["bug_y"]
        setscreen()
        sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])
    elif key_code == curses.KEY_LEFT:
        state["bug_x"] = 7 if state["bug_x"] == 0 else state["bug_x"] - 1
        state["bug_y"] = state["bug_y"] 
        setscreen()
        sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])

# Initial state
setscreen()
sense.set_pixel(state["bug_x"], state["bug_y"], state["bug_rgb"])

def get_keys(_):
    'Read one character from the keyboard and move bug'

    print("Press **Enter** or click the joystick to quit", flush=True)

    ## A blocking single char read in raw mode. 
    while True:
        char = s.getch()
        print('You entered char {0} \r'.format(char))
        draw_bug(char)
    return char

## Must init curses before calling any functions
s = curses.initscr()
## To make sure the terminal returns to its initial settings,
## and to set raw mode and guarantee cleanup on exit. 
curses.wrapper(get_keys)




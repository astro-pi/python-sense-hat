from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
native_str = str
str = type('')

import io
import os
import glob
import errno
import struct
import select
import random 
from collections import namedtuple
from threading import Thread, Event
from sense_hat import SenseHat 
from types import MethodType


InputEvent = namedtuple('InputEvent', ('timestamp', 'key', 'state'))


class SenseStick(object):
    SENSE_HAT_EVDEV_NAME = 'Raspberry Pi Sense HAT Joystick'
    EVENT_FORMAT = native_str('llHHI')
    EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

    EV_KEY = 0x01

    STATE_RELEASE = 0
    STATE_PRESS = 1
    STATE_HOLD = 2

    KEY_UP = 103
    KEY_LEFT = 105
    KEY_RIGHT = 106
    KEY_DOWN = 108
    KEY_ENTER = 28

    def __init__(self):
        self._stick_file = io.open(self._stick_device(), 'rb')

    def close(self):
        self._stick_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def __iter__(self):
        while True:
            event = self._stick_file.read(self.EVENT_SIZE)
            (tv_sec, tv_usec, type, code, value) = struct.unpack(self.EVENT_FORMAT, event)
            if type == self.EV_KEY:
                yield InputEvent(tv_sec + (tv_usec / 1000000), code, value)

    def _stick_device(self):
        for evdev in glob.glob('/sys/class/input/event*'):
            try:
                with io.open(os.path.join(evdev, 'device', 'name'), 'r') as f:
                    if f.read().strip() == self.SENSE_HAT_EVDEV_NAME:
                        return os.path.join('/dev', 'input', os.path.basename(evdev))
            except IOError as e:
                if e.errno != errno.ENOENT:
                    raise
        raise RuntimeError('unable to locate SenseHAT joystick device')

    def read(self):
        return next(iter(self))

    def wait(self, timeout=0):
        # Timeout of 0 means poll.
        r, w, x = select.select([self._stick_file], [], [], timeout)
        return bool(r)

class ClickStick(SenseStick):
    """
    Subclass of SenseStick that allows setting functions
    that will be run if any of the five Joystick inputs are 
    detected.
    
    The intent of the class is to avoid the boilerplate associated
    with responding to joystick events.
    
    Example Usage:
    
    ```
    # Instantiate
    stick = ClickStick()
    
    # Make a function that takes no arguments
    def custom_left():
        print("This happens when you click left!")
    
    # Set it to be called
    stick.on_left(custom_left)  # Note this is the function name,
                                # not a call to the function.
    # Listen for Joystick
    while True:
        stick.listen()
    ```
    
    In about 6 lines of code, moving the joystick left will 
    print "This happens when you click left!"
    
    Note that stick.listen() must be in a loop to be continuous. It 
    is non-blocking thanks to the polling features of SenseStick.

    The ClickStick will use an annonymous SenseHat instance, or you
    can provide your own:
    
    ~~~
    sense = SenseHat()
    sense.rotation = 90
    
    stick = ClickStick(sense)
    # stick will now use your rotated SenseHat object
    ~~~
    
    """

    def __init__(self, sense = None):
        SenseStick.__init__(self)
        # Create anonymous SenseHat unless one was provided
        self.sense = SenseHat() if sense == None else sense

    def _on_up(self):
        """Internal. Set by on_up and called by .listen"""
        r = self.sense.rotation
        self.sense.set_rotation((r + 90) % 360)
        self.sense.show_message("<=")
        self.sense.set_rotation(r)

    def _on_down(self):
        """Internal. Set by on_down and called by .listen"""
        r = self.sense.rotation
        self.sense.set_rotation((r + 270) % 360)
        self.sense.show_message("<=")
        self.sense.set_rotation(r)

    def _on_right(self):
        """Internal. Set by on_right and called by .listen"""
        r = sense.rotation
        self.sense.set_rotation((r + 180) % 360)    
        self.sense.show_message("<=")
        self.sense.set_rotation(r)

    def _on_left(self):
        """Internal. Set by on_left and called by .listen"""
        self.sense.show_message("<=")

    def _on_click(self):
        """Internal. Set by on_click and called by .listen"""
        self.sense.show_message("Click!")
        
    def on_up(self, func):
        """Takes a func and sets that to be called when the
        listen method detects a joystick down press"""
        def meth(self):
            func()
        self._on_up = MethodType(meth, self)

    def on_down(self, func):
        """Takes a func and sets that to be called when the
        listen method detects a joystick down press"""
        def meth(self):
            func()
        self._on_down = MethodType(meth, self)

    def on_right(self, func):
        """Takes a func and sets that to be called when the
        listen method detects a joystick right press"""
        def meth(self):
            func()
        self._on_right = MethodType(meth, self)

    def on_left(self, func):
        """Takes a func and sets that to be called when the
        listen method detects a joystick left press"""
        def meth(self):
            func()
        self._on_left = MethodType(meth, self)

    def on_click(self, func):
        """Takes a func and sets that to be called when the
        listen method detects a joystick click"""
        def meth(self):
            func()
        self._on_click = MethodType(meth, self)

    def listen(self):
        """Polls for events then calls the appropriate internal
        method."""
        # If there's a keypress to deal with (non-blocking)...
        if self.wait(0):
            # ...read it (blocking).
            key = self.read()
            
            # Extract key code
            key_code = key[1]
            
            if key[2] == self.STATE_RELEASE:
                # Ignore releases
                return
            
            # Do the appropriate thing.
            elif key_code == self.KEY_UP:
                self._on_up()
            elif key_code == self.KEY_DOWN:
                self._on_down()
            elif key_code == self.KEY_RIGHT:
                self._on_right()
            elif key_code == self.KEY_LEFT:
                self._on_left()
            elif key_code == self.KEY_ENTER:
                self._on_click()
    
if __name__ == "__main__":                
    """Demo. Move bug with joystick. Click to change background
    colo[u]r."""

    sense = SenseHat()
    stick = ClickStick(sense)

    bgcolor = (150,150,0)
    color = (210,210,210)
    position = [3,4]
    
    def left():
        global position
        sense.clear(bgcolor)
        x, y = position
        x = 7 if x == 0 else x -1
        position = [x,y]
        sense.set_pixel(x, y, color)
    
    def right():
        global position
        sense.clear(bgcolor)
        x, y = position
        x = 0 if x == 7 else x + 1
        position = [x,y]
        sense.set_pixel(x, y, color)
    
    def up():
        global position
        sense.clear(bgcolor)
        x, y = position
        y = 7 if y == 0 else y -1
        position = [x,y]
        sense.set_pixel(x, y, color)
    
    def down():
        global position
        sense.clear(bgcolor)
        x, y = position
        y = 0 if y == 7 else y + 1
        position = [x,y]
        sense.set_pixel(x, y, color)
    
    def click():
        global bgcolor
        r = randint(50,200)
        g = randint(50,200)
        bgcolor = (r,g,0)
        sense.clear(bgcolor)
        x, y = position
        sense.set_pixel(x, y, color)
      

    stick.on_up(up)
    stick.on_down(down)
    stick.on_right(right)
    stick.on_left(left)
    stick.on_click(click)
    
    sense.clear(bgcolor)
    x, y = position
    sense.set_pixel(x, y, color)
    
    while True:
        stick.listen()
    


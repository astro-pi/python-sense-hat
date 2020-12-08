from __future__ import absolute_import
from .sense_hat import SenseHat, SenseHat as AstroPi
from .stick import (
    SenseStick,
    InputEvent,
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_LEFT,
    DIRECTION_RIGHT,
    DIRECTION_MIDDLE,
    ACTION_PRESSED,
    ACTION_RELEASED,
    ACTION_HELD,
    )
from .tcs34725 import TCS34725, TCS34725 as ColourSensor
__version__ = '2.3.0'

import sense_hat
import time

"""
    Simple utility to test SenseHat joystick and LEDs are working.
    
    Uses sense_hat.SenseStick for input
"""

stick = sense_hat.SenseStick()
screen = sense_hat.SenseHat()

def react(event):
  n = event[1] + (event[1] - 100) * 10
  color = [(n,n,n)]*64
  screen.set_pixels(color)
  if press[1] == stick.KEY_RIGHT:
    print("Right!")
  elif press[1] == stick.KEY_LEFT:
    print("Left!")
  elif press[1] == stick.KEY_UP:
    print("UP!")
  elif press[1] == stick.KEY_DOWN:
    print("Down!")

print("Test joystick directions. Click joystick to exit")

while True:
  press = stick.read()
  if press[1] == stick.KEY_ENTER:
    break
  react(press)
  time.sleep(.001)



# Button-LED -- CircuitPython style on Arduino Uno
#
# digitalio INPUT with pull-up plus OUTPUT in the same sketch.
#
# Wiring: button between D2 and GND (internal pull-up); LED built-in on D13.
# Behaviour: hold button -> LED on; release -> LED off.
#
import board
import time
from digitalio import DigitalInOut, Direction, Pull


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    btn = DigitalInOut(board.D2)
    btn.switch_to_input(pull=Pull.UP)

    while True:
        # Button is active-low (pressed = False).
        led.value = not btn.value
        time.sleep(0.01)

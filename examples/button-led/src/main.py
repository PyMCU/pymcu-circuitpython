# Button-LED — CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  — board.D2 and board.LED resolved at compile time
#   digitalio     — INPUT with pull-up and OUTPUT in the same sketch
#   time module   — sleep_ms() for debounce
#
# Wiring:
#   Button: one leg to D2, other leg to GND (internal pull-up active)
#   LED:    built-in LED on D13 (no external wiring needed)
#
# Expected behaviour:
#   Hold button → LED on
#   Release button → LED off
#
import board
import time
from digitalio import DigitalInOut, Direction, Pull
from whipsnake.types import uint8


def main():
    led = DigitalInOut(board.LED)
    led.set_direction(Direction.OUTPUT)

    btn = DigitalInOut(board.D2)
    btn.set_direction(Direction.INPUT)
    btn.set_pull(Pull.UP)

    while True:
        state: uint8 = btn.get_value()
        # Button is active-low (pressed = 0)
        if state == 0:
            led.set_value(1)
        else:
            led.set_value(0)
        time.sleep_ms(10)

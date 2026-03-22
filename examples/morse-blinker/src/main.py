# Morse Blinker -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.LED resolved at compile time
#   digitalio     -- OUTPUT pin
#   time module   -- sleep_ms() for symbol timing
#   @inline       -- dot() and dash() helpers inlined at each call site
#                    (DigitalInOut is ZCA -- cannot be passed to non-inline functions)
#
# Wiring:
#   No external wiring needed -- uses the built-in LED on D13
#
# Timing (standard Morse, 1 dit = 200 ms):
#   dot  = 200 ms ON,  200 ms OFF
#   dash = 600 ms ON,  200 ms OFF
#   letter gap = 400 ms extra silence (600 ms total after last symbol)
#   word gap   = 1200 ms extra silence (1400 ms total after last letter)
#
# Output: SOS ( ... --- ... ) repeated indefinitely
#
import board
import time
from digitalio import DigitalInOut, Direction
from whisnake.types import inline


@inline
def dot(led):
    led.set_value(1)
    time.sleep_ms(200)
    led.set_value(0)
    time.sleep_ms(200)


@inline
def dash(led):
    led.set_value(1)
    time.sleep_ms(600)
    led.set_value(0)
    time.sleep_ms(200)


def main():
    led = DigitalInOut(board.LED)
    led.set_direction(Direction.OUTPUT)

    while True:
        # S: dot dot dot
        dot(led)
        dot(led)
        dot(led)
        time.sleep_ms(400)   # letter gap

        # O: dash dash dash
        dash(led)
        dash(led)
        dash(led)
        time.sleep_ms(400)   # letter gap

        # S: dot dot dot
        dot(led)
        dot(led)
        dot(led)
        time.sleep_ms(1200)  # word gap before repeat

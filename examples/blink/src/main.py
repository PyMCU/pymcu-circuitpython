# Blink -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.LED resolves to "PB5" at compile time
#   digitalio     -- DigitalInOut ZCA class, Direction constant
#   time module   -- sleep() with float seconds (folded at compile time)
#
# Wiring:
#   No external wiring needed -- uses the built-in LED on D13
#
# Expected behaviour:
#   LED toggles at 1 Hz (500 ms per half-period) indefinitely
#
import board
import digitalio
from time import sleep


def main():
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    while True:
        led.toggle()
        sleep(0.5)

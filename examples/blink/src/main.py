# Blink -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.LED resolves to "PB5" at compile time
#   digitalio     -- DigitalInOut, Direction, value property
#   time module   -- sleep() with float seconds (folded at compile time)
#
# Wiring: none -- uses the built-in LED on D13.
# Behaviour: LED blinks at 1 Hz (500 ms on, 500 ms off).
#
import board
import digitalio
from time import sleep


def main():
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    while True:
        led.value = True
        sleep(0.5)
        led.value = False
        sleep(0.5)

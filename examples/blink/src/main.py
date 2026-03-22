# Blink — CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  — board.LED resolves to "PB5" at compile time
#   digitalio     — DigitalInOut ZCA class, Direction constants
#   time module   — sleep_ms() with no hardware timer dependency
#
# Wiring:
#   No external wiring needed — uses the built-in LED on D13
#
# Expected behaviour:
#   LED blinks at 1 Hz (500 ms on / 500 ms off) indefinitely
#
import board
import digitalio
import time


def main():
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    while True:
        led.value = True
        time.sleep(0.15)
        led.value = False
        time.sleep(0.75)

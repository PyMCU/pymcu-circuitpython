# expect: build
# source: CircuitPython time.monotonic loop timing idiom
import time
import board
import digitalio

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
deadline = time.monotonic()

while True:
    now = time.monotonic()
    if now >= deadline:
        led.value = not led.value
        deadline = now + 0.5

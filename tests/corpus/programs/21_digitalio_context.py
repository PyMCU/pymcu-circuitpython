# expect: build
# source: CircuitPython digitalio docs context manager lifetime style
import time
import board
import digitalio

with digitalio.DigitalInOut(board.LED) as led:
    led.direction = digitalio.Direction.OUTPUT
    while True:
        led.value = not led.value
        time.sleep(0.25)

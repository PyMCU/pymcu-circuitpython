# expect: build
# source: Adafruit Learn CircuitPython Essentials digital input button style
import time
import board
import digitalio

button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = not button.value
    time.sleep(0.01)

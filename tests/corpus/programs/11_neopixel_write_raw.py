# expect: build
# source: CircuitPython neopixel_write module docs low-level buffer write
import time
import board
import digitalio
import neopixel_write

pin = digitalio.DigitalInOut(board.D6)
pin.direction = digitalio.Direction.OUTPUT
pixels = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0])

while True:
    pixels[0] = 0
    pixels[1] = 64
    pixels[2] = 0
    neopixel_write.neopixel_write(pin, pixels)
    time.sleep(0.5)

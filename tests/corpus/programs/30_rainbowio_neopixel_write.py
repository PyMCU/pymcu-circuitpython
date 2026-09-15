# expect: build
# source: CircuitPython rainbowio colorwheel plus neopixel_write style
import time
import board
import digitalio
import neopixel_write
from rainbowio import colorwheel

pin = digitalio.DigitalInOut(board.D6)
pin.direction = digitalio.Direction.OUTPUT
buf = bytearray(3)
pos = 0

while True:
    color = colorwheel(pos)
    buf[0] = (color >> 8) & 0xFF
    buf[1] = (color >> 16) & 0xFF
    buf[2] = color & 0xFF
    neopixel_write.neopixel_write(pin, buf)
    pos = (pos + 1) & 0xFF
    time.sleep(0.02)

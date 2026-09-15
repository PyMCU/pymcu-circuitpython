# expect: build
# source: Adafruit Learn NeoPixel CircuitPython fill tuple style
import time
import board
import neopixel

pixels = neopixel.NeoPixel(board.D6, 8, brightness=0.2, auto_write=False)

while True:
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(0.5)
    pixels.fill((0, 0, 255))
    pixels.show()
    time.sleep(0.5)

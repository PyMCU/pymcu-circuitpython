# Addressable NeoPixel -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   neopixel module -- NeoPixel(pin, n, auto_write=False)
#   fill((r, g, b))     -- set the whole strip to one colour
#   pixels[i] = (r,g,b) -- address an individual pixel (SRAM framebuffer)
#   show()              -- latch the framebuffer to the strip
#   time module         -- sleep() with float seconds (folded at compile time)
#
# Wiring: WS2812 / NeoPixel strip DIN -> D6, 5V -> 5V, GND -> GND.
#         (For more than a few pixels, power the strip from a separate 5V
#          supply and share grounds.)
# Behaviour: a single green pixel runs back and forth along the strip.
#
import board
import neopixel
from time import sleep

NUM = 8


def main():
    # auto_write=False: build the whole frame in the buffer, then show() once.
    pixels = neopixel.NeoPixel(board.D6, NUM, auto_write=False)

    while True:
        # Sweep the lit pixel from the first to the last.
        i = 0
        while i < NUM:
            pixels.fill((0, 0, 0))      # clear every pixel
            pixels[i] = (0, 32, 0)      # light pixel i green (addressable)
            pixels.show()               # latch the frame
            sleep(0.08)
            i = i + 1

        # Sweep back from the last to the first.
        i = NUM - 2
        while i > 0:
            pixels.fill((0, 0, 0))
            pixels[i] = (0, 32, 0)
            pixels.show()
            sleep(0.08)
            i = i - 1

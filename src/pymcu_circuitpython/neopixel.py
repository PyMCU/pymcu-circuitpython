# CircuitPython-compatible neopixel module for PyMCU
#
# Provides a NeoPixel class that mirrors CircuitPython's neopixel.NeoPixel API.
#
# Usage (CircuitPython style):
#   import board
#   import neopixel
#
#   pixels = neopixel.NeoPixel(board.D6, 8)      # pin, count
#   pixels.fill((255, 0, 0))                      # fill all red
#   pixels[0] = (0, 255, 0)                       # set pixel 0 to green
#   pixels.show()                                  # latch
#
# Note: The NeoPixel class uses the pymcu.drivers.neopixel driver
#       which sends WS2812 GRB protocol. Global interrupts must be disabled
#       during show() for correct timing; the driver handles this internally.
#
# Limitations:
#   - Individual pixel indexing (pixels[i] = ...) is compile-time constant only.
#   - brightness scaling is not supported (zero-overhead constraint).
#   - auto_write is accepted but always False on bare metal (manual show() required).

from pymcu.types import uint8, uint16, inline, const
from pymcu.drivers.neopixel import NeoPixel as _NeoPixel
from pymcu.types import asm


RGB  = 0
GRB  = 1
RGBW = 2


class NeoPixel:
    """CircuitPython-compatible NeoPixel LED strip driver.

    Parameters:
        pin        -- board pin constant (e.g. board.D6) or raw pin string ("PD6")
        n          -- number of pixels in the strip
        bpp        -- bytes per pixel; 3 (RGB/GRB) supported; 4 (RGBW) accepted but
                      the W channel is silently ignored on WS2812 hardware
        brightness -- accepted for API compatibility; not applied (zero-overhead constraint)
        auto_write -- accepted for API compatibility; always treated as False
        pixel_order -- GRB (1) or RGB (0); default GRB matches WS2812 hardware
    """

    @inline
    def __init__(self, pin, n: uint8, bpp: uint8 = 3, brightness: uint8 = 1,
                 auto_write: uint8 = 0, pixel_order: uint8 = GRB):
        self._strip = _NeoPixel(pin, n)
        self._n = n
        self._order = pixel_order

    @inline
    def __len__(self) -> uint8:
        """Return number of pixels in the strip."""
        return self._n

    @property
    def brightness(self) -> uint8:
        """Brightness level (1 = full, stored for API compatibility; not scaled on bare metal)."""
        return 1

    @inline
    def fill(self, r: uint8, g: uint8, b: uint8):
        """Fill all pixels with (r, g, b). Call show() to latch."""
        i: uint8 = 0
        while i < self._n:
            self._strip.set_pixel(r, g, b)
            i = i + 1

    @inline
    def set_pixel(self, index: uint8, r: uint8, g: uint8, b: uint8):
        """Set a single pixel by index. Non-addressable: writes all pixels up to index."""
        i: uint8 = 0
        while i <= index:
            self._strip.set_pixel(r, g, b)
            i = i + 1

    @inline
    def show(self):
        """Latch pixel data by sending the WS2812 reset pulse."""
        asm("CLI")
        self._strip.show()
        asm("SEI")

    @inline
    def deinit(self):
        """Release the NeoPixel resource (no-op on bare metal)."""
        pass

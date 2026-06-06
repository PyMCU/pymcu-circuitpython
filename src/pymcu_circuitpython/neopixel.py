# CircuitPython-compatible neopixel module for PyMCU
#
# Provides a NeoPixel class that mirrors CircuitPython's neopixel.NeoPixel API
# for the common whole-strip fill use case.
#
# Usage (CircuitPython style):
#   import board
#   import neopixel
#
#   pixels = neopixel.NeoPixel(board.D6, 8)
#   pixels.fill(0xFF0000)        # all red (0xRRGGBB packed colour)
#   # with auto_write (default True) the strip latches immediately;
#   # otherwise call pixels.show()
#
# Colour order constants (match the CircuitPython names).
RGB  = "RGB"
GRB  = "GRB"
RGBW = "RGBW"
GRBW = "GRBW"

from pymcu.types import uint8, uint32, inline, asm, warning
from pymcu.drivers.neopixel import NeoPixel as _NeoPixel


class NeoPixel:
    """CircuitPython-compatible WS2812 NeoPixel strip (whole-strip fill).

    Parameters mirror CircuitPython:
        pin         -- board pin constant (e.g. board.D6) or raw pin string
        n           -- number of pixels in the strip
        bpp         -- bytes per pixel (3 RGB / 4 RGBW; W ignored on WS2812)
        brightness  -- 0.0-1.0; accepted for API compatibility (see note)
        auto_write  -- latch automatically after a write (default True)
        pixel_order -- colour channel order; GRB is the WS2812 default

    Limitations (bare-metal): see fill()/__setitem__ for why individual pixel
    addressing and per-pixel brightness scaling are not supported here.
    """

    @inline
    def __init__(self, pin, n: uint8, bpp: uint8 = 3, brightness: float = 1.0,
                 auto_write: uint8 = 1, pixel_order=None):
        self._strip = _NeoPixel(pin, n)
        self._n = n
        self._auto_write = auto_write

    @inline
    def __len__(self) -> uint8:
        """Number of pixels in the strip."""
        return self._n

    @property
    def n(self) -> uint8:
        """Number of pixels in the strip (read-only)."""
        return self._n

    @property
    def auto_write(self) -> uint8:
        """Whether writes latch automatically."""
        return self._auto_write

    @property
    def brightness(self) -> float:
        """Strip brightness (1.0 = full).

        Returned as a float literal for API compatibility. Per-pixel brightness
        scaling is not applied: it would require buffering and scaling every
        pixel, which the zero-overhead immediate-write driver does not do.
        """
        return 1.0

    @inline
    def fill(self, color: uint32):
        """Set every pixel to a single packed 0xRRGGBB colour.

        With auto_write enabled (the default) the strip latches immediately.
        Note: CircuitPython also accepts an (r, g, b) tuple here; on PyMCU pass
        the packed integer form (e.g. 0xFF8000) -- tuple colour literals are not
        yet supported as call arguments by the compiler.
        """
        r: uint8 = (color >> 16) & 0xFF
        g: uint8 = (color >> 8) & 0xFF
        b: uint8 = color & 0xFF
        # WS2812 timing is cycle-exact: keep interrupts disabled for the whole
        # transmission (all pixels + the latch/reset pulse).
        asm("CLI")
        i: uint8 = 0
        while i < self._n:
            self._strip.set_pixel(r, g, b)
            i = i + 1
        self._strip.show()
        asm("SEI")

    @warning("neopixel individual pixel assignment (pixels[i] = color) needs a per-strip SRAM framebuffer; it is a no-op here. Use fill(color) to set the whole strip.")
    def __setitem__(self, index, color):
        pass

    @inline
    def show(self):
        """Send the WS2812 reset/latch pulse."""
        asm("CLI")
        self._strip.show()
        asm("SEI")

    @inline
    def deinit(self):
        """Release the NeoPixel resource (no-op on bare metal)."""
        pass

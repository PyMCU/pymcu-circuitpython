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
#   pixels.fill((255, 0, 0))     # all red ((r, g, b) tuple, as in CircuitPython)
#   # with auto_write (default True) the strip latches immediately;
#   # otherwise call pixels.show()
#
# Colour order constants (match the CircuitPython names).
RGB  = "RGB"
GRB  = "GRB"
RGBW = "RGBW"
GRBW = "GRBW"

from pymcu.types import uint8, uint16, inline, asm
from pymcu.drivers.neopixel import NeoPixel as _NeoPixel


class NeoPixel:
    """CircuitPython-compatible WS2812 NeoPixel strip with addressable pixels.

    Parameters mirror CircuitPython:
        pin         -- board pin constant (e.g. board.D6) or raw pin string
        n           -- number of pixels in the strip
        bpp         -- bytes per pixel (3 RGB; W is ignored on WS2812)
        brightness  -- 0.0-1.0; accepted for API compatibility (see note)
        auto_write  -- latch automatically after a write (default True)
        pixel_order -- colour channel order; GRB is the WS2812 default

    Colours are held in a per-strip SRAM framebuffer (3 bytes/pixel in WS2812
    wire order), so both whole-strip fill((r, g, b)) and individual
    pixels[i] = (r, g, b) are supported, exactly as in CircuitPython.
    """

    @inline
    def __init__(self, pin, n: uint8, bpp: uint8 = 3, brightness: float = 1.0,
                 auto_write: uint8 = 1, pixel_order=None):
        self._strip = _NeoPixel(pin, n)
        self._n = n
        self._auto_write = auto_write
        # Per-strip SRAM framebuffer, 3 bytes/pixel, WS2812 wire (GRB) order.
        # The compiler reserves a fixed uint8[n*3] array from the annotation and
        # ignores the initialiser; the bytearray() makes the same attribute a
        # real, indexable buffer under CPython simulation.
        self._buf: uint8[n*3] = bytearray(n * 3)

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
    def fill(self, color):
        """Set every pixel to a single (r, g, b) colour (CircuitPython fill()).

        Pass an (r, g, b) tuple, exactly as in CircuitPython:
        pixels.fill((255, 0, 0)). The channels are written into the framebuffer
        in WS2812 wire (GRB) order. With auto_write enabled (the default) the
        strip latches immediately.

        Note: CircuitPython's fill() also accepts a packed 0xRRGGBB integer.
        That alternative form is not simultaneously dispatchable here because an
        integer literal and a tuple literal are indistinguishable to the @inline
        overload resolver, so the canonical tuple form is the supported one.
        """
        g: uint8 = color[1]
        r: uint8 = color[0]
        b: uint8 = color[2]
        i: uint8 = 0
        while i < self._n:
            base: uint16 = i * 3
            self._buf[base + 0] = g
            self._buf[base + 1] = r
            self._buf[base + 2] = b
            i = i + 1
        if self._auto_write:
            self.show()

    @inline
    def __setitem__(self, index, color):
        """Set pixel `index` to an (r, g, b) tuple (CircuitPython pixels[i] = ...).

        Writes the colour into the per-strip SRAM framebuffer in WS2812 wire
        (GRB) order. With auto_write enabled (the default) the strip latches
        immediately; otherwise the change appears on the next show().
        """
        base: uint16 = index * 3
        self._buf[base + 0] = color[1]   # G
        self._buf[base + 1] = color[0]   # R
        self._buf[base + 2] = color[2]   # B
        if self._auto_write:
            self.show()

    @inline
    def show(self):
        """Stream the framebuffer to the strip and send the WS2812 latch pulse.

        Interrupts are disabled for the whole transmission because WS2812 bit
        timing is cycle-exact.
        """
        asm("CLI")
        total: uint16 = self._n * 3
        i: uint16 = 0
        while i < total:
            self._strip.write_byte(self._buf[i])
            i = i + 1
        self._strip.show()
        asm("SEI")

    @inline
    def deinit(self):
        """Release the NeoPixel resource (no-op on bare metal)."""
        pass

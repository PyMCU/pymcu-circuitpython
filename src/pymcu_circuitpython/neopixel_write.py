# CircuitPython-compatible neopixel_write module for PyMCU
#
#   import board, digitalio, neopixel_write
#
#   pin = digitalio.DigitalInOut(board.D6)
#   pin.direction = digitalio.Direction.OUTPUT
#   neopixel_write.neopixel_write(pin, bytearray([0, 255, 0]))   # one red pixel
#
# This is the low-level call a great many published guides make directly, below the
# `neopixel` library. CircuitPython's signature is
# `neopixel_write(digitalinout: DigitalInOut, buf: ReadableBuffer) -> None`, and the
# bytes go out in the strip's own order, which for a WS2812 is green, red, blue. The
# buffer is not reordered here; what the caller passes is what reaches the wire.
#
# The timing lives in `pymcu.hal.ws2812`, not here. There is no clock line on this
# protocol, so a one is told from a zero by how long the pin stays high -- 375 ns
# against 812 ns, with 150 ns of margin -- and how a part manages that is the part's
# business: counted NOPs on an AVR, a PIO program on an RP2040. Nothing about any of
# them appears in this file, which is why it is the same file for every target.
#
# INTERRUPTS. CircuitPython masks them for the length of the frame. This does not,
# and the caller owns it, because the only architecture-neutral primitives PyMCU has
# are `enable_interrupts` and `disable_interrupts` with nothing that reads the flag
# first: re-enabling at the end would switch interrupts ON for a program that had
# deliberately turned them off. An interrupt taken mid-byte stretches one high time
# past its tolerance and that pixel latches the wrong colour, so a program with a
# timer running should bracket the call itself. See PyMCU#353.

from pymcu.types import inline
from pymcu.hal.ws2812 import ws2812_init, ws2812_write_byte, ws2812_reset


@inline
def neopixel_write(digitalinout, buf):
    """Write `buf` to the one-wire pixels on `digitalinout`, then latch.

    `digitalinout` is a `digitalio.DigitalInOut`, as in CircuitPython, rather than a
    pin name: that is the object every guide has in hand at this point, and taking a
    name instead would make this the one call in the layer that does not.

    `buf` is anything the compiler can walk a byte at a time -- a `bytes` or
    `bytearray` literal, which unrolls, or a fixed-size `uint8` array, which loops.
    """
    # The pin the DigitalInOut was built on. It is a compile-time name, so the port
    # and bit it selects fold out of the emitter and what is left is one SBI/CBI pair.
    pin = digitalinout._pin.name

    # Drive the line low before the frame. The caller has already set the direction
    # via `switch_to_output()` or `.direction`, but a line left high reads as the
    # front of a bit, and this is also where an unsupported pin is refused by name.
    ws2812_init(pin)

    for b in buf:
        ws2812_write_byte(pin, b)

    # More than 50 us low: the strip takes that as end-of-frame and shows what it got.
    ws2812_reset(pin)

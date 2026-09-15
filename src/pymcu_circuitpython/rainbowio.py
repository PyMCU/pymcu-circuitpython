# CircuitPython-compatible rainbowio module for PyMCU
#
#   from rainbowio import colorwheel
#
#   pixels[i] = colorwheel(n)
#
# One function, and it is arithmetic: no pin, no peripheral, nothing architecture-specific,
# so there is no HAL half to this module.

from pymcu.types import uint8, uint32, inline


@inline
def colorwheel(n: uint8) -> uint32:
    """A colour from a position on the wheel, as the 0xRRGGBB integer a pixel takes.

    The wheel runs red, green, blue and back to red across 0 to 255, which is the mapping
    every Adafruit example's `wheel()` has:

    | n | red | green | blue | colour |
    |---|---|---|---|---|
    | 0 | 255 | 0 | 0 | red |
    | 85 | 0 | 255 | 0 | green |
    | 170 | 0 | 0 | 255 | blue |
    | 255 | 255 | 0 | 0 | back to red |

    Between those, one channel falls by 3 per step while the next rises by 3.

    `n` is a byte, so there is no out-of-range case to return black for: CircuitPython
    takes any integer and gives black outside 0 to 255, and a value that cannot leave the
    range cannot reach that branch.
    """
    if n < 85:
        return (uint32(255 - n * 3) << 16) | (uint32(n * 3) << 8)
    if n < 170:
        return (uint32(255 - (n - 85) * 3) << 8) | uint32((n - 85) * 3)
    return (uint32((n - 170) * 3) << 16) | uint32(255 - (n - 170) * 3)

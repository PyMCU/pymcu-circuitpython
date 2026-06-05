# CircuitPython-compatible time module for PyMCU
#
# Provides sleep(), sleep_ms(), and sleep_us() that map directly to
# the underlying PyMCU delay functions (no runtime overhead).
#
# Usage:
#   import time
#   time.sleep(0.5)        # 500 ms (float seconds; folded at compile time)
#   time.sleep_ms(500)     # 500 ms
#   time.sleep_us(100)     # 100 us

from pymcu.types import uint8, uint16, uint32, inline
from pymcu.time import delay_ms, delay_us


@inline
def sleep(seconds: float):
    # Accept a float (e.g. 0.5) and fold seconds*1000 to ms at compile time.
    delay_ms(uint16(seconds * 1000))


@inline
def sleep_ms(ms: uint16):
    delay_ms(ms)


@inline
def sleep_us(us: uint8):
    delay_us(us)


@inline
def monotonic() -> uint32:
    """Seconds since power-on (integer approximation of float seconds).

    On AVR: wraps millis() / 1000. Wraps at ~4294967 seconds (~49 days).
    Note: CircuitPython returns a float; PyMCU returns a uint32 integer.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() // 1000


@inline
def monotonic_ns() -> uint32:
    """Nanoseconds since power-on (uint32 approximation).

    On AVR: wraps millis() * 1_000_000. Wraps at ~4294 seconds (~71 min).
    Suitable for short-duration sub-second measurements.
    Note: CircuitPython returns a large integer; PyMCU returns a uint32.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() * 1000000

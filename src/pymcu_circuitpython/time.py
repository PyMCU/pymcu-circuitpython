# CircuitPython-compatible time module for PyMCU
#
# Provides the CircuitPython time API: sleep(), monotonic() and monotonic_ns().
#
# Usage:
#   import time
#   time.sleep(0.5)              # 500 ms (float seconds; folded at compile time)
#   t = time.monotonic()         # seconds since boot (float)

from pymcu.types import uint16, uint32, inline, warning


@inline
def sleep(seconds: float):
    """Sleep for the given number of (fractional) seconds.

    The seconds value is multiplied by 1000 and folded to an integer
    millisecond delay at compile time (e.g. sleep(0.5) -> delay_ms(500)).
    """
    from pymcu.time import delay_ms
    delay_ms(uint16(seconds * 1000))


@inline
@warning("time.monotonic() uses the software floating-point runtime (no hardware FPU on AVR).")
def monotonic() -> float:
    """Seconds since power-on as a float (matches CircuitPython).

    On AVR: millis() / 1000.0 using the soft-float runtime.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() / 1000.0


@inline
def monotonic_ns() -> uint32:
    """Nanoseconds since power-on, as an integer (CircuitPython returns int).

    On AVR the underlying counter is 32-bit, so millis()*1_000_000 wraps after
    ~4.29 seconds. This is a hardware range limitation, not an API/type
    deviation; suitable for short sub-second interval measurements.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() * 1000000

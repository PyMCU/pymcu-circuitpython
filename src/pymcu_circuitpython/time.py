# CircuitPython-compatible time module for PyMCU
#
# Provides the CircuitPython time API: sleep(), monotonic() and monotonic_ns().
#
# Usage:
#   import time
#   time.sleep(0.5)              # 500 ms (float seconds; folded at compile time)
#   t = time.monotonic()         # seconds since boot (float)

from pymcu.types import uint8, uint16, uint32, inline, warning


@inline
def sleep(seconds: float):
    """Sleep for the given number of (fractional) seconds.

    Two things this could not do before. It went through a 16-bit millisecond count, so
    anything past 65.535 seconds wrapped -- sleep(120) slept 54.5 -- and anything under a
    millisecond rounded to zero, so sleep(0.0005) did not sleep at all.

    Now the whole duration is taken in microseconds, the seconds are paid out in chunks the
    delay can hold, and the remainder is paid in microseconds. With a literal duration, which
    is what a CircuitPython program writes, the whole thing folds to the chunks it needs.
    """
    from pymcu.time import delay_ms, delay_us
    total_us: uint32 = uint32(seconds * 1000000.0)
    whole_ms: uint32 = total_us // 1000
    while whole_ms > 60000:
        delay_ms(60000)
        whole_ms = whole_ms - 60000
    if whole_ms != 0:
        delay_ms(uint16(whole_ms))
    rest_us: uint16 = uint16(total_us - (total_us // 1000) * 1000)
    while rest_us > 200:
        delay_us(200)
        rest_us = rest_us - 200
    if rest_us != 0:
        delay_us(uint8(rest_us))


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

    It WRAPS after 4.295 seconds, and there is no way around it here: CircuitPython's
    integers are arbitrary precision and the widest one this compiler has is 32 bits, which
    holds 4.295e9 nanoseconds. A difference between two readings taken less than that apart
    is still exact, which is what an interval measurement needs; a reading treated as an
    absolute time is wrong as soon as the program has run for five seconds.

    For a clock that does not wrap for 49 days, use monotonic() (float seconds) or
    supervisor.ticks_ms().
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() * 1000000

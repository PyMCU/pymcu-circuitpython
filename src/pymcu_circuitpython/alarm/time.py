# CircuitPython-compatible alarm.time submodule for PyMCU
#
# Provides TimeAlarm: wake at an absolute time.monotonic() timestamp (seconds).
# A real module, not a singleton instance -- upstream spells it
# `import alarm.time` / `alarm.time.TimeAlarm`, and alarm/__init__.py binds the
# submodule under `time` so both spellings land here.

from pymcu.types import uint32, inline


class TimeAlarm:
    """Wake at an absolute time.monotonic() timestamp (in seconds)."""

    @inline
    def __init__(self, monotonic_time: float = 0.0):
        # Start the millisecond time base. A TimeAlarm waits on millis(), and the build
        # starts that clock only for a program that names ticks_ms, monotonic or asyncio
        # itself: a program whose only use of time is an alarm got a counter that never
        # moved, so the alarm never fired and sleep never returned.
        # Programming it twice is programming it the same way twice.
        from pymcu.hal.timer import millis_init as _millis_init
        _millis_init()
        self._is_time = 1
        # The deadline in whole milliseconds, worked out once here. The wait is a
        # comparison against the millisecond counter, so the soft-float arithmetic
        # happens at construction instead of on every pass of the polling loop.
        self._deadline_ms = uint32(monotonic_time * 1000.0)
        self._pin_name = ""
        self._value = 0

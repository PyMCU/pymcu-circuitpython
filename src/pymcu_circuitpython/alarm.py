# CircuitPython-compatible alarm module for PyMCU
#
# Provides alarm.time.TimeAlarm, alarm.pin.PinAlarm and the
# sleep_until_alarms()/light_sleep_until_alarms() entry points.
#
# Usage (CircuitPython style):
#   import alarm, time, board
#
#   # Wake 60 seconds from now (monotonic_time is an ABSOLUTE timestamp):
#   ta = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
#   alarm.sleep_until_alarms(ta)
#
#   # Wake when D2 goes high:
#   pa = alarm.pin.PinAlarm(board.D2, value=True)
#   alarm.sleep_until_alarms(pa)
#
# Implementation notes:
#   - TimeAlarm.monotonic_time matches CircuitPython exactly: it is an absolute
#     time.monotonic() value, NOT a duration. sleep_until_alarms() sleeps for
#     (monotonic_time - time.monotonic()) seconds. This uses the soft-float
#     runtime (see @warning) because time.monotonic() returns float seconds.
#   - There is no true low-power deep sleep on AVR here: TimeAlarm blocks in a
#     delay and PinAlarm polls the pin. light_sleep_until_alarms() is an alias.
#   - The triggered alarm is recorded in alarm.wake_alarm.

from pymcu.types import uint8, uint16, inline, warning
from pymcu.time import delay_ms
from pymcu.hal.gpio import Pin as _Pin


wake_alarm = None


# -- alarm.time submodule -----------------------------------------------------

class _TimeAlarmModule:
    """Namespace for alarm.time.TimeAlarm (mirrors CircuitPython's alarm.time)."""

    class TimeAlarm:
        """Wake at an absolute time.monotonic() timestamp (in seconds)."""

        @inline
        def __init__(self, monotonic_time: float = 0.0):
            self._time = monotonic_time
            self._is_time = 1


time = _TimeAlarmModule()


# -- alarm.pin submodule ------------------------------------------------------

class _PinAlarmModule:
    """Namespace for alarm.pin.PinAlarm (mirrors CircuitPython's alarm.pin)."""

    class PinAlarm:
        """Wake when a pin reaches a logic level.

        Parameters:
            pin   -- board pin constant (e.g. board.D2) or raw pin string
            value -- True to wake on HIGH, False to wake on LOW
            edge  -- accepted for API compatibility; AVR uses level polling here
            pull  -- accepted for API compatibility (configure pulls via digitalio)
        """

        @inline
        def __init__(self, pin, value: uint8 = 1, edge: uint8 = 0, pull: uint8 = 0):
            self._pin_name = pin
            self._value    = value
            self._is_time  = 0


pin = _PinAlarmModule()


# -- Top-level sleep functions ------------------------------------------------

@inline
@warning("alarm.sleep_until_alarms() uses the software floating-point runtime for TimeAlarm timing.")
def sleep_until_alarms(alarm_obj) -> uint8:
    """Block until the given alarm fires.

    TimeAlarm: sleeps until alarm_obj's absolute monotonic_time is reached.
    PinAlarm:  polls the pin until it matches the requested level.

    The concrete alarm type is known at compile time (ZCA), so the unused
    branch is eliminated -- only the relevant path is emitted.
    """
    if alarm_obj._is_time:
        from pymcu.hal.timer import millis as _millis
        # monotonic_time is absolute seconds; convert the remaining time to ms.
        now_s: float = _millis() / 1000.0
        remaining_s: float = alarm_obj._time - now_s
        if remaining_s > 0.0:
            delay_ms(uint16(remaining_s * 1000.0))
        return 0

    _p = _Pin(alarm_obj._pin_name, _Pin.IN)
    while True:
        if alarm_obj._value:
            if _p.value():
                return 0
        else:
            if _p.value() == 0:
                return 0


@inline
@warning("alarm.light_sleep_until_alarms() uses the software floating-point runtime for TimeAlarm timing.")
def light_sleep_until_alarms(alarm_obj) -> uint8:
    """Light-sleep variant -- identical to sleep_until_alarms() on AVR."""
    return sleep_until_alarms(alarm_obj)


@inline
@warning("alarm.exit_and_deep_sleep_until_alarms() has no true deep sleep on AVR; it blocks until the alarm like light sleep (RAM is retained, the program continues instead of restarting).")
def exit_and_deep_sleep_until_alarms(alarm_obj) -> uint8:
    """Deep-sleep entry point (CircuitPython alarm.exit_and_deep_sleep_until_alarms).

    CircuitPython powers the chip down and restarts from scratch when the alarm
    fires. AVR has no equivalent low-power-with-reset path here, so this blocks
    until the alarm exactly like light_sleep_until_alarms() and then returns to
    the caller. The triggered alarm is still recorded in alarm.wake_alarm.
    """
    return sleep_until_alarms(alarm_obj)

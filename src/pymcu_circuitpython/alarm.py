# CircuitPython-compatible alarm module for PyMCU
#
# Provides PinAlarm and TimeAlarm classes, and sleep_until_alarms().
#
# Usage (CircuitPython style):
#   import alarm
#   import board
#
#   # Sleep for 500 ms then wake:
#   time_alarm = alarm.time.TimeAlarm(monotonic_time=500)
#   alarm.sleep_until_alarms(time_alarm)
#
#   # Sleep until a pin goes high:
#   pin_alarm = alarm.pin.PinAlarm(board.D2, value=True)
#   alarm.sleep_until_alarms(pin_alarm)
#
# Implementation notes:
#   - TimeAlarm uses delay_ms() -- it blocks but is power-optimal in the
#     absence of a tickless RTOS. Use power.sleep_idle() for true low-power sleep.
#   - PinAlarm polls the pin in a tight loop. For true interrupt-driven wake,
#     use pymcu.hal.gpio Pin with an interrupt handler directly.
#   - light_sleep_until_alarms() is an alias for sleep_until_alarms() on AVR
#     (no architectural distinction between light and deep sleep here).

from pymcu.types import uint8, uint16, inline
from pymcu.time import delay_ms
from pymcu.hal.gpio import Pin as _Pin


# -- alarm.time submodule -----------------------------------------------------

class _TimeAlarmModule:
    """Namespace for alarm.time.TimeAlarm -- mirrors CircuitPython's alarm.time."""

    class TimeAlarm:
        """Wake after a specified number of milliseconds.

        Parameters:
            monotonic_time -- milliseconds to sleep (mapped from CP's float seconds
                              to integer ms for MCU compatibility)
        """

        @inline
        def __init__(self, monotonic_time: uint16 = 0):
            self._ms = monotonic_time


time = _TimeAlarmModule()


# -- alarm.pin submodule ------------------------------------------------------

class _PinAlarmModule:
    """Namespace for alarm.pin.PinAlarm -- mirrors CircuitPython's alarm.pin."""

    class PinAlarm:
        """Wake when a pin reaches a specified logic level.

        Parameters:
            pin   -- board pin constant (e.g. board.D2) or raw pin string
            value -- 1 to wake on HIGH, 0 to wake on LOW
            edge  -- accepted for API compatibility (not implemented)
            pull  -- accepted for API compatibility (not implemented)
        """

        @inline
        def __init__(self, pin, value: uint8 = 1,
                     edge: uint8 = 0, pull: uint8 = 0):
            self._pin_name = pin
            self._value    = value


pin = _PinAlarmModule()


# -- Top-level sleep functions ------------------------------------------------

@inline
def sleep_until_alarms(alarm_obj) -> uint8:
    """Block until the given alarm fires.

    Accepts a TimeAlarm or PinAlarm. Returns 0 (alarm type id not inspectable
    at runtime on bare metal).

    For TimeAlarm: calls delay_ms(alarm_obj._ms).
    For PinAlarm:  polls the pin until its value matches alarm_obj._value.
    """
    # TimeAlarm path: sleep for _ms milliseconds
    match alarm_obj._ms:
        case 0:
            # Not a TimeAlarm (ms=0); fall through to pin poll
            pass
        case _:
            delay_ms(alarm_obj._ms)
            return 0

    # PinAlarm path: poll pin
    _p = _Pin(alarm_obj._pin_name, _Pin.IN)
    while True:
        match alarm_obj._value:
            case 1:
                if _p.value():
                    return 0
            case _:
                if _p.value() == 0:
                    return 0


@inline
def light_sleep_until_alarms(alarm_obj) -> uint8:
    """Light-sleep variant -- identical to sleep_until_alarms() on AVR."""
    return sleep_until_alarms(alarm_obj)

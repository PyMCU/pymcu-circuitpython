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

from pymcu.types import uint8, uint16, uint32, inline, warning
from pymcu.time import delay_ms
from pymcu.hal.gpio import Pin as _Pin


# CircuitPython sets wake_alarm to the alarm object that woke the board. There is nowhere
# to put an object in a module global here -- an instance assigned to one loses what it is --
# so this stays None and the alarm that fired comes back as the RETURN VALUE of
# sleep_until_alarms(), which is its position in the argument list. A program that reads
# wake_alarm expecting an alarm gets None, which is what it would get on a board that woke
# from the reset button, so it is at least a value upstream produces.
wake_alarm = None


# -- alarm.time submodule -----------------------------------------------------

class _TimeAlarmModule:
    """Namespace for alarm.time.TimeAlarm (mirrors CircuitPython's alarm.time)."""

    class TimeAlarm:
        """Wake at an absolute time.monotonic() timestamp (in seconds)."""

        @inline
        def __init__(self, monotonic_time: float = 0.0):
            # Start the millisecond time base. A TimeAlarm waits on millis(), and the build
            # starts that clock only for a program that names ticks_ms, monotonic or asyncio
            # itself: a program whose only use of time is an alarm got a counter that never
            # moved, so the alarm never fired and sleep_until_alarms never returned.
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
            self._is_time     = 0
            self._deadline_ms = 0
            self._pin_name    = pin
            self._value       = value


pin = _PinAlarmModule()


# -- Top-level sleep functions ------------------------------------------------

# Has this one alarm's condition come true yet? One pass, no waiting.
#
# The two arms both read fields the other type also has, so a mixed set of alarms can be
# polled in one loop. A TimeAlarm carries an empty pin name and a PinAlarm a deadline of
# zero, and the arm that is not taken folds away wherever the alarm's type is known.
@inline
def _alarm_fired(alarm_obj) -> uint8:
    if alarm_obj._is_time:
        from pymcu.hal.timer import millis as _millis
        if _millis() >= alarm_obj._deadline_ms:
            return 1
        return 0
    else:
        _p = _Pin(alarm_obj._pin_name, _Pin.IN)
        if alarm_obj._value:
            if _p.value():
                return 1
            return 0
        if _p.value() == 0:
            return 1
        return 0


@inline
@warning("alarm.sleep_until_alarms() uses the software floating-point runtime for TimeAlarm timing.")
def sleep_until_alarms(alarm0, alarm1=None, alarm2=None, alarm3=None) -> uint8:
    """Block until one of the given alarms fires, and return WHICH.

    It took one alarm and returned a constant 0, so a program waiting on "a time limit or a
    button" could only wait on one of the two, and could not have told them apart if it had
    waited on both. Up to four are polled in turn now, and the return value is the position
    of the one that fired: 0 for the first, 1 for the second, and so on.

    CircuitPython returns the alarm OBJECT and also puts it in alarm.wake_alarm. Neither is
    possible here -- an instance handed back from a function, or assigned to a module global,
    loses what it is -- so the position is what comes back. `if alarm.sleep_until_alarms(ta,
    pa) == 1:` is the shape a program writes.

    There is no true low-power sleep on this part: a TimeAlarm waits on the millisecond
    counter and a PinAlarm polls its pin, both with the CPU running.
    """
    while True:
        if _alarm_fired(alarm0):
            return 0
        match alarm1:
            case None:
                pass
            case _:
                if _alarm_fired(alarm1):
                    return 1
        match alarm2:
            case None:
                pass
            case _:
                if _alarm_fired(alarm2):
                    return 2
        match alarm3:
            case None:
                pass
            case _:
                if _alarm_fired(alarm3):
                    return 3


@inline
@warning("alarm.light_sleep_until_alarms() uses the software floating-point runtime for TimeAlarm timing.")
def light_sleep_until_alarms(alarm0, alarm1=None, alarm2=None, alarm3=None) -> uint8:
    """Light-sleep variant -- identical to sleep_until_alarms() on AVR."""
    return sleep_until_alarms(alarm0, alarm1, alarm2, alarm3)


@inline
@warning("alarm.exit_and_deep_sleep_until_alarms() has no true deep sleep on AVR; it blocks until the alarm like light sleep (RAM is retained, the program continues instead of restarting).")
def exit_and_deep_sleep_until_alarms(alarm0, alarm1=None, alarm2=None, alarm3=None) -> uint8:
    """Deep-sleep entry point (CircuitPython alarm.exit_and_deep_sleep_until_alarms).

    CircuitPython powers the chip down and restarts from scratch when the alarm
    fires. AVR has no equivalent low-power-with-reset path here, so this blocks
    until the alarm exactly like light_sleep_until_alarms() and then returns to
    the caller, with the position of the alarm that fired.
    """
    return sleep_until_alarms(alarm0, alarm1, alarm2, alarm3)

# CircuitPython-compatible alarm module for PyMCU
#
# Provides alarm.time.TimeAlarm, alarm.pin.PinAlarm (real submodules, the same
# shape upstream has: `import alarm.time` / `alarm.time.TimeAlarm`) and the
# light_sleep_until_alarms()/exit_and_deep_sleep_until_alarms() entry points.
#
# Usage (CircuitPython style):
#   import alarm, time, board
#
#   # Wake 60 seconds from now (monotonic_time is an ABSOLUTE timestamp):
#   ta = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
#   alarm.light_sleep_until_alarms(ta)
#
#   # Wake when D2 goes high:
#   pa = alarm.pin.PinAlarm(board.D2, value=True)
#   alarm.light_sleep_until_alarms(pa)
#
# Implementation notes:
#   - TimeAlarm.monotonic_time matches CircuitPython exactly: it is an absolute
#     time.monotonic() value, NOT a duration. light_sleep_until_alarms() sleeps
#     for (monotonic_time - time.monotonic()) seconds. This uses the soft-float
#     runtime (see @warning) because time.monotonic() returns float seconds.
#   - There is no true low-power deep sleep on AVR here: TimeAlarm blocks in a
#     delay and PinAlarm polls the pin. exit_and_deep_sleep_until_alarms() is an
#     alias that returns to the caller instead of restarting the program.
#   - CircuitPython has no sleep_until_alarms() -- only the light_ and
#     exit_and_deep_ spellings. The unqualified name existed here once and was
#     removed: a name that exists here but not on a board is the failure this
#     layer exists to prevent.
#   - The triggered alarm is recorded in alarm.wake_alarm.

from pymcu.types import uint8, inline, warning
from pymcu.hal.gpio import Pin as _Pin

# Upstream these are real modules, so `alarm.time.TimeAlarm` after `import
# alarm` must resolve. `from . import` binds the submodule on the instance that
# is executing this file -- under CPython the layer can be loaded under two
# names (`pymcu_circuitpython.alarm` and the bare `alarm` alias), and each has
# to carry the attribute itself. `import alarm.time` is the spelling the PyMCU
# compiler needs to register the submodule for member access.
from . import time
from . import pin
import alarm.time
import alarm.pin


# CircuitPython sets wake_alarm to the alarm object that woke the board. There is nowhere
# to put an object in a module global here -- an instance assigned to one loses what it is --
# so this stays None and the alarm that fired comes back as the RETURN VALUE of
# light_sleep_until_alarms(), which is its position in the argument list. A program that
# reads wake_alarm expecting an alarm gets None, which is what it would get on a board
# that woke from the reset button, so it is at least a value upstream produces.
wake_alarm = None


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
@warning("alarm.light_sleep_until_alarms() uses the software floating-point runtime for TimeAlarm timing.")
def light_sleep_until_alarms(*alarms) -> uint8:
    """Block until one of the given alarms fires, and return WHICH.

    It took one alarm and returned a constant 0, so a program waiting on "a time limit or a
    button" could only wait on one of the two, and could not have told them apart if it had
    waited on both. Any number are polled in turn now -- *alarms is the upstream
    signature -- and the return value is the position of the one that fired: 0 for the
    first, 1 for the second, and so on.

    CircuitPython returns the alarm OBJECT and also puts it in alarm.wake_alarm. Neither is
    possible here -- an instance handed back from a function, or assigned to a module global,
    loses what it is -- so the position is what comes back. `if
    alarm.light_sleep_until_alarms(ta, pa) == 1:` is the shape a program writes.

    There is no true low-power sleep on this part: a TimeAlarm waits on the millisecond
    counter and a PinAlarm polls its pin, both with the CPU running.
    """
    while True:
        i: uint8 = 0
        for a in alarms:
            if _alarm_fired(a):
                return i
            i = i + 1


@inline
@warning("alarm.exit_and_deep_sleep_until_alarms() has no true deep sleep on AVR; it blocks until the alarm like light sleep (RAM is retained, the program continues instead of restarting).")
def exit_and_deep_sleep_until_alarms(*alarms, preserve_dios=()) -> uint8:
    """Deep-sleep entry point (CircuitPython alarm.exit_and_deep_sleep_until_alarms).

    CircuitPython powers the chip down and restarts from scratch when the alarm
    fires; preserve_dios keeps digital pins configured across the reset. AVR has
    no equivalent low-power-with-reset path here, so this blocks until the alarm
    exactly like light_sleep_until_alarms() and then returns to the caller, with
    the position of the alarm that fired. preserve_dios is accepted for
    signature compatibility and ignored.
    """
    return light_sleep_until_alarms(*alarms)

# CircuitPython-compatible alarm.pin submodule for PyMCU
#
# Provides PinAlarm: wake when a pin reaches a logic level. A real module, not
# a singleton instance -- upstream spells it `import alarm.pin` /
# `alarm.pin.PinAlarm`, and alarm/__init__.py binds the submodule under `pin`
# so both spellings land here.

from pymcu.types import uint8, inline


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

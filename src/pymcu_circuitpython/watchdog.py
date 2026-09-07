# CircuitPython-compatible `watchdog` module.
#
# Upstream puts WatchDogMode here, not in `microcontroller`. microcontroller
# keeps the `watchdog` object itself, which is where upstream has it.
"""CircuitPython `watchdog` compatibility module."""

class WatchDogMode:
    """Watchdog modes, as CircuitPython's watchdog.WatchDogMode.

    AVR supports system-reset only; RAISE (interrupt) is
    defined for API compatibility but behaves as RESET on this target.
    """
    RESET = 0
    RAISE = 1

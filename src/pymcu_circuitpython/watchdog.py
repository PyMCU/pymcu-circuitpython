# CircuitPython-compatible `watchdog` module.
#
# Upstream puts WatchDogMode here, not in `microcontroller`. microcontroller
# keeps the `watchdog` object itself, which is where upstream has it.
"""CircuitPython `watchdog` compatibility module."""

class WatchDogMode:
    """Watchdog modes, as CircuitPython's watchdog.WatchDogMode.

    RESET is what the AVR's watchdog does: the part restarts. RAISE fires an interrupt
    instead and lets the program keep running, and this HAL does not program that, so asking
    for it is refused where it is written rather than quietly giving a reset -- a program
    that expects to catch a WatchDogTimeout and recover would instead reboot, which is the
    opposite of what it asked for.

    `watchdog.mode = None` disables the watchdog, as upstream allows.
    """
    RESET = 1
    RAISE = 2


# watchdog.WatchDogTimer is the class of the sole instance at microcontroller.watchdog.
# The class itself lives in microcontroller.py, next to the instance it backs and the HAL
# calls its methods make; this just re-exports it under its upstream name, the same way
# microcontroller.py imports WatchDogMode from here below.
from microcontroller import WatchDogTimer

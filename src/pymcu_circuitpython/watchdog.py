# CircuitPython-compatible `watchdog` module.
#
# Upstream puts WatchDogMode and WatchDogTimer both here; microcontroller.py imports
# WatchDogTimer from this module to build the microcontroller.watchdog singleton. The
# reverse used to be true (this module imported WatchDogTimer from microcontroller.py,
# which imported WatchDogMode back from here) and the compiler refused it as a cyclic
# import: unlike CPython, it needs a DAG of module dependencies to build its compilation
# tree, and tolerates none of the partial-module tricks a two-way import relies on under
# CPython. The class lives where nothing it needs lives on the other side of the cycle.
"""CircuitPython `watchdog` compatibility module."""

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, inline, warning


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


class WatchDogTimer:
    """Hardware watchdog (CircuitPython microcontroller.watchdog / WatchDogTimer).

    Set .timeout (seconds), then assign .mode = WatchDogMode.RESET to arm the
    watchdog; call .feed() before it expires, or .deinit() to disable it. The
    timeout is a runtime value, armed via the const-free HAL path (arm_ms), so
    it may come from a variable rather than a compile-time literal.

    `mode = None` disables the watchdog and `mode = WatchDogMode.RESET` arms it, as
    upstream. RAISE is refused: this HAL does not program the interrupt mode, and arming a
    reset for a program that asked to catch a timeout and recover is the opposite of what
    it asked for.
    """

    @inline
    def __init__(self):
        self._timeout_ms = 1000
        self._mode = 0

    @property
    @warning("microcontroller.watchdog.timeout uses the software floating-point runtime (seconds <-> ms conversion).")
    def timeout(self) -> float:
        return self._timeout_ms / 1000.0

    @timeout.setter
    def timeout(self, seconds: float):
        self._timeout_ms = uint16(seconds * 1000.0)

    @property
    def mode(self) -> uint8:
        return self._mode

    @mode.setter
    def mode(self, m):
        """Arm or disable the watchdog.

        It armed for ANY value, including the None that upstream uses to disable it, and
        `mode = None` did not compile at all: the setter took a uint8 and None is not one.
        Now None disables, RESET arms, and RAISE is refused because this HAL does not
        program the interrupt mode and a program that asked to catch a timeout would
        instead have been rebooted.
        """
        from pymcu.hal.watchdog import Watchdog
        match m:
            case None:
                self._mode = 0
                Watchdog().disable()
            case WatchDogMode.RESET:
                self._mode = 1
                Watchdog().arm_ms(self._timeout_ms)
            case WatchDogMode.RAISE:
                raise CompileError(
                    "the watchdog's RAISE mode fires an interrupt and lets the program carry "
                    "on, and this HAL programs only the reset mode. Use "
                    "watchdog.WatchDogMode.RESET, which restarts the part, or feed the "
                    "watchdog from a place that can tell whether the program is still "
                    "healthy. Accepting RAISE would have rebooted a program that asked to "
                    "recover.")
            case _:
                raise CompileError(
                    "a watchdog mode is watchdog.WatchDogMode.RESET, or None to disable it.")

    @inline
    def feed(self):
        from pymcu.hal.watchdog import Watchdog
        Watchdog().feed()

    @inline
    def deinit(self):
        from pymcu.hal.watchdog import Watchdog
        Watchdog().disable()

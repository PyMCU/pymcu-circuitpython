# CircuitPython-compatible supervisor module for PyMCU
#
# Provides a minimal subset of CircuitPython's supervisor module.
#
# Usage:
#   import supervisor
#   ms = supervisor.ticks_ms()      # milliseconds since boot (16-bit counter)
#   supervisor.reload()             # software reset via watchdog

from pymcu.types import uint16, inline
from pymcu.time import delay_ms


@inline
def ticks_ms() -> uint16:
    """Returns a 16-bit millisecond counter (wraps at 65535).

    On AVR this is a software counter incremented by the compiler runtime.
    Not suitable for long-duration timing; use delay_ms() for that.
    Note: In PyMCU, this returns 0 as the compiler does not maintain
    a system tick counter by default. Use pymcu.hal.timer for precise timing.
    """
    # Compile-time constant 0 -- a proper tick counter requires a timer interrupt.
    return 0


@inline
def reload():
    """Perform a software reset of the microcontroller.

    Triggers an immediate reset via the watchdog timer with the shortest
    timeout (15 ms).
    """
    from pymcu.hal.watchdog import Watchdog as _Watchdog
    wd = _Watchdog()
    wd.enable()
    # Spin until the watchdog fires
    while True:
        pass


# Runtime status flags (compile-time constants on bare metal)
runtime = None

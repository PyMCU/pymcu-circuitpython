# CircuitPython-compatible supervisor module for PyMCU
#
# Provides a minimal subset of CircuitPython's supervisor module.
#
# Usage:
#   import supervisor
#   ms = supervisor.ticks_ms()      # milliseconds since boot (16-bit counter)
#   supervisor.reload()             # software reset via watchdog

from pymcu.types import uint8, uint16, uint32, inline
from pymcu.time import delay_ms


@inline
def ticks_ms() -> uint32:
    """Milliseconds since power-on (uint32, wraps at ~49 days).

    On AVR: uses Timer0 millis() counter. Requires millis_init() to have been
    called at startup; the PyMCU build driver injects this automatically when
    ticks_ms() is detected in user code.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis()


@inline
def ticks_add(ticks: uint32, delta: uint32) -> uint32:
    """Add delta to ticks, wrapping at the 32-bit boundary.

    Compatible with CircuitPython's supervisor.ticks_add().
    """
    return ticks + delta


@inline
def ticks_diff(new_ticks: uint32, old_ticks: uint32) -> uint32:
    """Compute elapsed milliseconds between two ticks_ms() readings.

    Returns (new_ticks - old_ticks), handling uint32 wrap-around.
    Note: CircuitPython uses a 29-bit counter; here we use 32-bit.
    """
    return new_ticks - old_ticks


@inline
def reload():
    """Perform a software reset of the microcontroller.

    Triggers an immediate reset via the watchdog timer with the shortest
    timeout (15 ms).
    """
    from pymcu.hal.watchdog import Watchdog as _Watchdog
    wd = _Watchdog()
    wd.enable()
    while True:
        pass


# Runtime status flags (compile-time constants on bare metal)
runtime = None

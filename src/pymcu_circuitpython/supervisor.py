# CircuitPython-compatible supervisor module for PyMCU
#
# Mirrors CircuitPython's supervisor timing helpers exactly, including the
# 2**29 ms wrap of ticks_ms() and the signed, wrap-aware ticks_diff().
#
# Usage:
#   import supervisor
#   start = supervisor.ticks_ms()
#   # ... later ...
#   elapsed = supervisor.ticks_diff(supervisor.ticks_ms(), start)  # signed ms
#   supervisor.reload()             # software reset via watchdog

from pymcu.types import uint32, int32, inline


# CircuitPython ticks are kept modulo 2**29 so the arithmetic stays correct on
# boards without long integers.  ticks_diff() returns a *signed* value assuming
# the two readings are within 2**28 ms of each other.  These constants and the
# helper bodies match the canonical CircuitPython reference implementation.
_TICKS_PERIOD     = 1 << 29
_TICKS_MAX        = _TICKS_PERIOD - 1
_TICKS_HALFPERIOD = _TICKS_PERIOD // 2


@inline
def ticks_ms() -> uint32:
    """Milliseconds since power-on, wrapping at 2**29 (matches CircuitPython).

    On AVR: uses the Timer0 millis() counter, masked to 29 bits so the value
    and all ticks_add()/ticks_diff() arithmetic behave exactly as documented
    for CircuitPython.  Requires millis_init() at startup; the PyMCU build
    driver injects it automatically when ticks_ms() is detected.
    """
    from pymcu.hal.timer import millis as _millis
    return _millis() & _TICKS_MAX


@inline
def ticks_add(ticks: uint32, delta: uint32) -> uint32:
    """Add delta to a ticks value, wrapping modulo 2**29 (CircuitPython parity)."""
    return (ticks + delta) % _TICKS_PERIOD


@inline
def ticks_diff(ticks1: uint32, ticks2: uint32) -> int32:
    """Signed elapsed milliseconds between two ticks_ms() readings.

    Returns ticks1 - ticks2 as a signed value in the range [-2**28, 2**28),
    correctly handling the 2**29 wrap.  Identical semantics to CircuitPython's
    supervisor.ticks_diff().
    """
    diff: int32 = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff


@inline
def reload():
    """Reload and restart the program (software reset via watchdog).

    On bare metal there is no REPL to return to, so this performs an immediate
    MCU reset using the watchdog with the shortest timeout, which re-runs the
    program from the reset vector -- the closest equivalent to CircuitPython's
    supervisor.reload().
    """
    from pymcu.hal.watchdog import Watchdog as _Watchdog
    wd = _Watchdog()
    wd.enable()
    while True:
        pass


# -- supervisor.runtime -------------------------------------------------------
# CircuitPython exposes a Runtime singleton with USB/REPL status flags.  A
# bare-metal firmware has no USB stack or REPL, so these are reported as
# compile-time constants: a hardware UART is always "ready" to talk, but there
# is no USB enumeration and no REPL byte queue to inspect.  Code that polls
# these flags compiles and runs; the values reflect the bare-metal reality.

class _Runtime:
    @property
    def serial_connected(self) -> uint32:
        # A hardware UART is always available on bare metal.
        return 1

    @property
    def usb_connected(self) -> uint32:
        # No USB device stack in a bare-metal firmware.
        return 0

    @property
    def serial_bytes_available(self) -> uint32:
        # No supervisor-managed console queue; use busio.UART.in_waiting for
        # actual received-byte counts on the hardware UART.
        return 0


runtime = _Runtime()

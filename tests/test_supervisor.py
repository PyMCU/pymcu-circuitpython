"""supervisor: the 2**29 ticks_ms wrap (CircuitPython parity)."""
from unittest.mock import patch
import pymcu.hal.timer as _tm
from pymcu_circuitpython import supervisor
from pymcu_circuitpython.supervisor import ticks_ms

_PERIOD = 1 << 29
_MAX = _PERIOD - 1


def test_ticks_ms_masked_to_29bits():
    with patch.object(_tm, "millis", return_value=5000):
        assert ticks_ms() == 5000
    with patch.object(_tm, "millis", return_value=_PERIOD + 7):
        assert ticks_ms() == 7   # wraps at 2**29


def test_ticks_add_and_diff_are_not_provided():
    # Upstream CircuitPython's supervisor has ticks_ms and nothing else of this
    # family: its docs present ticks_add/ticks_diff as example code the caller
    # writes, and those spellings are MicroPython's. A compat layer that accepts
    # them lets non-portable code compile here and fail on a board, so they were
    # removed. This test is the guard against them coming back.
    assert not hasattr(supervisor, "ticks_add")
    assert not hasattr(supervisor, "ticks_diff")


def test_wrap_aware_elapsed_is_still_expressible():
    # The arithmetic the helpers used to wrap up, written the way upstream's
    # docs show it: mask the difference back into the tick period.
    assert (2 - _MAX) & _MAX == 3
    assert (5 - 3) & _MAX == 2


def test_runtime_flags():
    assert supervisor.runtime.serial_connected == 1
    assert supervisor.runtime.usb_connected == 0


def test_serial_bytes_available_asks_the_uart():
    # It was a constant zero, so `while not serial_bytes_available:` never ended.
    from unittest.mock import patch
    import pymcu.hal.uart as _u
    with patch.object(_u.UART, "available", return_value=1):
        assert supervisor.runtime.serial_bytes_available == 1

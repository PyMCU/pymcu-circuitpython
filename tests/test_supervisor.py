"""supervisor: 2**29 ticks_ms wrap and signed ticks_diff (CircuitPython parity)."""
from unittest.mock import patch
import pymcu.hal.timer as _tm
from pymcu_circuitpython import supervisor
from pymcu_circuitpython.supervisor import ticks_ms, ticks_add, ticks_diff

_PERIOD = 1 << 29
_MAX = _PERIOD - 1


def test_ticks_ms_masked_to_29bits():
    with patch.object(_tm, "millis", return_value=5000):
        assert ticks_ms() == 5000
    with patch.object(_tm, "millis", return_value=_PERIOD + 7):
        assert ticks_ms() == 7   # wraps at 2**29


def test_ticks_add_modular():
    assert ticks_add(_MAX, 5) == 4


def test_ticks_diff_basic():
    assert ticks_diff(5, 3) == 2
    assert ticks_diff(3, 5) == -2


def test_ticks_diff_handles_wrap():
    # 3 ms elapsed from just-before-wrap to just-after-wrap.
    assert ticks_diff(2, _MAX) == 3


def test_runtime_flags():
    assert supervisor.runtime.serial_connected == 1
    assert supervisor.runtime.usb_connected == 0

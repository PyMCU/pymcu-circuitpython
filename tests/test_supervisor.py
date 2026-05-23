from unittest.mock import patch
import pymcu.hal.timer as _timer_mod

from pymcu_circuitpython import supervisor


def test_ticks_ms_returns_int():
    t = supervisor.ticks_ms()
    assert isinstance(t, int)


def test_ticks_ms_delegates_to_millis():
    with patch.object(_timer_mod, "millis", return_value=1234):
        t = supervisor.ticks_ms()
    assert t == 1234


def test_ticks_ms_default_is_zero():
    # Default mock millis() returns 0
    assert supervisor.ticks_ms() == 0


def test_ticks_add_basic():
    result = supervisor.ticks_add(1000, 500)
    assert result == 1500


def test_ticks_add_zero_delta():
    result = supervisor.ticks_add(42, 0)
    assert result == 42


def test_ticks_add_large():
    result = supervisor.ticks_add(0xFFFFFFF0, 32)
    assert isinstance(result, int)


def test_ticks_diff_basic():
    result = supervisor.ticks_diff(1500, 1000)
    assert result == 500


def test_ticks_diff_zero():
    result = supervisor.ticks_diff(100, 100)
    assert result == 0


def test_ticks_diff_roundtrip():
    start = supervisor.ticks_ms()
    end = supervisor.ticks_add(start, 200)
    diff = supervisor.ticks_diff(end, start)
    assert diff == 200


def test_runtime_is_none():
    assert supervisor.runtime is None

"""time module: sleep(), monotonic() (float), monotonic_ns() (int)."""
from unittest.mock import patch
import pymcu.hal.timer as _tm
from pymcu_circuitpython.time import sleep, monotonic, monotonic_ns


def test_sleep_callable():
    sleep(0.5)
    sleep(0)


def test_monotonic_returns_float():
    assert isinstance(monotonic(), float)


def test_monotonic_value_from_millis():
    with patch.object(_tm, "millis", return_value=5000):
        assert monotonic() == 5.0


def test_monotonic_ns_returns_int():
    assert isinstance(monotonic_ns(), int)


def test_monotonic_ns_value_from_millis():
    with patch.object(_tm, "millis", return_value=1):
        assert monotonic_ns() == 1_000_000

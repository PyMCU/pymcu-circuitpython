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


def test_a_sleep_past_sixty_five_seconds_is_paid_in_chunks():
    # It went through a 16-bit millisecond count, so sleep(120) slept 54.5 s.
    import pymcu.time as _t
    from pymcu_circuitpython.time import sleep
    calls: list = []
    old_ms, old_us = _t.delay_ms, _t.delay_us
    _t.delay_ms = lambda ms: calls.append(("ms", ms))
    _t.delay_us = lambda us: calls.append(("us", us))
    try:
        sleep(120)
    finally:
        _t.delay_ms, _t.delay_us = old_ms, old_us
    assert sum(v for k, v in calls if k == "ms") == 120000
    assert all(v <= 65535 for k, v in calls if k == "ms")


def test_a_sleep_under_a_millisecond_is_paid_in_microseconds():
    # It rounded to zero milliseconds and did not sleep at all.
    import pymcu.time as _t
    from pymcu_circuitpython.time import sleep
    calls: list = []
    old_ms, old_us = _t.delay_ms, _t.delay_us
    _t.delay_ms = lambda ms: calls.append(("ms", ms))
    _t.delay_us = lambda us: calls.append(("us", us))
    try:
        sleep(0.0005)
    finally:
        _t.delay_ms, _t.delay_us = old_ms, old_us
    assert sum(v for k, v in calls if k == "us") == 500
    assert all(v <= 255 for k, v in calls if k == "us")

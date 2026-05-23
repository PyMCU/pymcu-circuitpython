from pymcu_circuitpython.time import sleep, sleep_ms, sleep_us


def test_sleep_callable():
    sleep(1)


def test_sleep_ms_callable():
    sleep_ms(500)


def test_sleep_us_callable():
    sleep_us(100)


def test_sleep_ms_zero():
    sleep_ms(0)


def test_sleep_large_value():
    sleep_ms(60000)


def test_monotonic_returns_int():
    from pymcu_circuitpython.time import monotonic
    t = monotonic()
    assert isinstance(t, int)


def test_monotonic_value_from_millis():
    import pymcu.hal.timer as _tm
    from unittest.mock import patch
    from pymcu_circuitpython.time import monotonic
    with patch.object(_tm, "millis", return_value=5000):
        t = monotonic()
    assert t == 5


def test_monotonic_ns_returns_int():
    from pymcu_circuitpython.time import monotonic_ns
    t = monotonic_ns()
    assert isinstance(t, int)


def test_monotonic_ns_value_from_millis():
    import pymcu.hal.timer as _tm
    from unittest.mock import patch
    from pymcu_circuitpython.time import monotonic_ns
    with patch.object(_tm, "millis", return_value=1):
        t = monotonic_ns()
    assert t == 1_000_000

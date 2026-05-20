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

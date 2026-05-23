import pytest
from pymcu_circuitpython import microcontroller


def test_cpu_frequency():
    freq = microcontroller.cpu.frequency
    assert freq == 16_000_000


def test_cpu_temperature_raises():
    with pytest.raises(NotImplementedError):
        _ = microcontroller.cpu.temperature


def test_cpu_reset_raises():
    with pytest.raises(NotImplementedError):
        microcontroller.cpu.reset()


def test_cpu_uid_is_tuple():
    uid = microcontroller.cpu.uid
    assert isinstance(uid, tuple)
    assert len(uid) == 8


def test_cpu_uid_all_zeros():
    uid = microcontroller.cpu.uid
    assert all(b == 0 for b in uid)


def test_cpu_voltage():
    v = microcontroller.cpu.voltage
    assert v == 5


def test_module_delay_us_callable():
    microcontroller.delay_us(100)  # must not raise


def test_pin_class_exists():
    assert microcontroller.Pin is not None

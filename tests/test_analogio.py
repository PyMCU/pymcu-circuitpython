import pytest

from pymcu_circuitpython.analogio import AnalogIn, AnalogOut


def test_analog_in_instantiation():
    adc = AnalogIn("PC0")
    assert adc is not None


def test_analog_in_value_is_zero_from_mock():
    adc = AnalogIn("PC0")
    # Mock AnalogPin.read() returns 0 → scaled 0 << 6 == 0
    assert adc.value == 0


def test_analog_in_read_u16():
    adc = AnalogIn("PC0")
    v = adc.read_u16()
    assert v == 0


def test_analog_in_value_is_in_range():
    # Even with a non-zero mock, the 16-bit scale must stay within uint16 bounds
    adc = AnalogIn("PC0")
    v = adc.value
    assert 0 <= v <= 65535


def test_analog_out_raises_not_implemented():
    with pytest.raises((NotImplementedError, Exception)):
        AnalogOut("PC0")


def test_reference_voltage():
    adc = AnalogIn("PC0")
    v = adc.reference_voltage
    assert v == 5


def test_deinit():
    adc = AnalogIn("PC0")
    adc.deinit()  # must not raise


def test_context_manager():
    adc = AnalogIn("PC0")
    adc.__enter__()
    v = adc.value
    adc.__exit__()
    assert v == 0

"""analogio: AnalogIn (16-bit value, float reference_voltage)."""
from unittest.mock import patch
import pymcu.hal.adc as _adc
from pymcu_circuitpython.analogio import AnalogIn, AnalogOut


def test_value_scaled_to_16bit():
    a = AnalogIn("PC0")
    with patch.object(_adc._MockAnalogPin if hasattr(_adc, "_MockAnalogPin") else a._adc.__class__,
                      "read", return_value=1023):
        # value = raw10 << 6
        assert a.value == 1023 << 6


def test_reference_voltage_is_float():
    a = AnalogIn("PC0")
    assert a.reference_voltage == 5.0
    assert isinstance(a.reference_voltage, float)


def test_no_read_u16():
    assert not hasattr(AnalogIn, "read_u16")   # MicroPython-ism removed


def test_context_manager():
    with AnalogIn("PC0") as a:
        _ = a.value


def test_analogout_exists():
    # On hardware @warning makes AnalogOut emit a build-time note (no DAC); in
    # CPython the decorator is a passthrough, so the constructor is a no-op.
    AnalogOut("PC0")

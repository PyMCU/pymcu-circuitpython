"""analogio: AnalogIn (16-bit value, float reference_voltage) and AnalogOut (refused with no DAC)."""
from unittest.mock import patch
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.analogio import AnalogIn, AnalogOut


def test_full_scale_reads_full_scale():
    # Scaling by 64 topped out at 65472: full scale on the pin was 63 counts short of full
    # scale in the number, so `value == 65535` never happened and volts came out low.
    a = AnalogIn("PC0")
    with patch.object(a._adc.__class__, "read", return_value=1023):
        assert a.value == 65535


def test_zero_reads_zero():
    a = AnalogIn("PC0")
    with patch.object(a._adc.__class__, "read", return_value=0):
        assert a.value == 0


def test_midscale_is_monotonic_and_close_to_half():
    a = AnalogIn("PC0")
    with patch.object(a._adc.__class__, "read", return_value=512):
        mid = a.value
    with patch.object(a._adc.__class__, "read", return_value=511):
        below = a.value
    assert below < mid
    assert abs(mid - 32768) <= 64


def test_reference_voltage_is_float_and_comes_from_the_hal():
    a = AnalogIn("PC0")
    assert a.reference_voltage == 5.0
    assert isinstance(a.reference_voltage, float)
    # The value is the HAL's, not a literal in the layer: a part with another reference
    # reports that one without this file changing.
    with patch.object(a._adc.__class__, "reference_volts", return_value=3.3):
        assert a.reference_voltage == 3.3


def test_no_read_u16():
    assert not hasattr(AnalogIn, "read_u16")   # MicroPython-ism removed


def test_context_manager():
    with AnalogIn("PC0") as a:
        _ = a.value


def test_analogout_is_refused_where_there_is_no_dac():
    # It used to build with a warning and compile the assignment to nothing, so a program
    # asking for an analog output ran and drove no pin.
    with pytest.raises(CompileError) as e:
        AnalogOut("PC0")
    assert "pwm" in str(e.value).lower()

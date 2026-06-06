"""microcontroller: cpu info, reset() via watchdog, soft-float temperature/voltage."""
from unittest.mock import patch
import pymcu.hal.adc as _adc
from pymcu_circuitpython import microcontroller
from pymcu_circuitpython.microcontroller import cpu


def test_frequency():
    assert cpu.frequency == 16_000_000


def test_uid_is_zero_tuple():
    assert cpu.uid == (0, 0, 0, 0, 0, 0, 0, 0)


def test_temperature_is_float():
    t = cpu.temperature
    assert isinstance(t, float)


def test_voltage_is_float():
    with patch.object(_adc.AnalogPin, "read", return_value=512):
        v = cpu.voltage
    assert isinstance(v, float)


def test_delay_us_callable():
    microcontroller.delay_us(100)


def test_nvm_len_is_eeprom_size():
    assert len(microcontroller.nvm) == 1024


def test_nvm_read_write_roundtrip():
    microcontroller.nvm[10] = 0x42
    assert microcontroller.nvm[10] == 0x42
    # A distinct address is independent.
    microcontroller.nvm[11] = 0x99
    assert microcontroller.nvm[10] == 0x42
    assert microcontroller.nvm[11] == 0x99


def test_nvm_masks_to_byte():
    microcontroller.nvm[5] = 0x1FF      # value masked to 8 bits in the store
    assert microcontroller.nvm[5] == 0xFF


def test_reset_uses_watchdog():
    # reset() arms the watchdog then spins; patch the loop guard away by making
    # Watchdog.enable raise so we don't loop forever.
    import pymcu.hal.watchdog as _wd

    class _Boom(Exception):
        pass

    class _WD:
        def __init__(self, timeout_ms=500): pass
        def enable(self):
            raise _Boom

    with patch.object(_wd, "Watchdog", _WD):
        try:
            microcontroller.reset()
        except _Boom:
            pass
        else:
            raise AssertionError("reset() did not arm the watchdog")

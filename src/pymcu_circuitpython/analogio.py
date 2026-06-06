# CircuitPython-compatible analogio module for PyMCU
#
# Provides AnalogIn (and a guarded AnalogOut) mirroring CircuitPython's
# analogio API.
#
# Usage (CircuitPython style):
#   from analogio import AnalogIn
#   import board
#
#   adc = AnalogIn(board.A0)
#   val = adc.value              # int, 0-65535 (scaled from the 10-bit ADC)
#   vref = adc.reference_voltage # float volts
#
# Note: CircuitPython's AnalogIn.value is 16-bit (0-65535). The AVR ADC is
#       10-bit (0-1023), so we scale by 64x to match CircuitPython behaviour.

from pymcu.types import uint16, inline, warning
from pymcu.hal.adc import AnalogPin as _AnalogPin


class AnalogIn:
    @inline
    def __init__(self, pin):
        self._adc = _AnalogPin(pin)

    @property
    def value(self) -> uint16:
        """Read the ADC scaled to 16-bit (0-65535) to match CircuitPython."""
        self._adc.start()
        raw10: uint16 = self._adc.read()
        return raw10 << 6  # Scale 10-bit to 16-bit

    @property
    def reference_voltage(self) -> float:
        """ADC reference voltage in volts (5.0 V on standard 5 V AVR boards).

        Returned as a compile-time float literal, so it folds away at zero cost.
        """
        return 5.0

    @inline
    def deinit(self):
        """Release the ADC resource (no-op on bare metal)."""
        pass

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()


class AnalogOut:
    """Analog (DAC) output -- not available on AVR (no DAC peripheral)."""

    @warning("analogio.AnalogOut requires a hardware DAC, which AVR targets do not have; this is a no-op. Use pwmio.PWMOut for an analog-like output.")
    @inline
    def __init__(self, pin):
        pass

# CircuitPython-compatible analogio module for Whipsnake
#
# Provides AnalogIn class that mirrors CircuitPython's analogio.AnalogIn API.
#
# Usage (CircuitPython style):
#   from analogio import AnalogIn
#   import board
#
#   adc = AnalogIn(board.A0)
#   val = adc.value          # uint16, 0-65535 (scaled from 10-bit ADC)
#   raw = adc.reference_voltage  # Not yet supported (requires float)
#
# Note: CircuitPython's AnalogIn.value returns a 16-bit value (0-65535).
#       AVR's ADC is 10-bit (0-1023), so we scale by 64x to match CP behavior.

from whipsnake.types import uint8, uint16, inline
from whipsnake.hal.adc import AnalogPin as _AnalogPin


class AnalogIn:
    @inline
    def __init__(self, pin_name):
        self._adc = _AnalogPin(pin_name)

    @property
    def value(self) -> uint16:
        """Read ADC value scaled to 16-bit (0-65535) to match CircuitPython."""
        # AVR ADC is 10-bit (0-1023), scale to 16-bit by shifting left 6 bits (multiply by 64)
        self._adc.start()
        # Poll ADCSRA[6] (ADSC) to wait for conversion
        # Then read ADCL/ADCH (implementation in AnalogPin.read())
        raw10: uint16 = self._adc.read()
        return raw10 << 6  # Scale 10-bit to 16-bit

    @inline
    def read_u16(self) -> uint16:
        """Alias for .value property (MicroPython compatibility)."""
        return self.value


class AnalogOut:
    """AnalogOut is not supported on AVR (no DAC)."""
    @inline
    def __init__(self, pin_name):
        # Raise compile-time error
        raise NotImplementedError("AnalogOut requires a DAC (not available on AVR)")

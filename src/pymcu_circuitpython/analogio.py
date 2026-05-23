# CircuitPython-compatible analogio module for PyMCU
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

from pymcu.types import uint8, uint16, inline
from pymcu.hal.adc import AnalogPin as _AnalogPin


class AnalogIn:
    @inline
    def __init__(self, pin_name):
        self._adc = _AnalogPin(pin_name)

    @property
    def value(self) -> uint16:
        """Read ADC value scaled to 16-bit (0-65535) to match CircuitPython."""
        self._adc.start()
        raw10: uint16 = self._adc.read()
        return raw10 << 6  # Scale 10-bit to 16-bit

    @property
    def reference_voltage(self) -> uint8:
        """Reference voltage in volts (5 V on standard 5 V AVR boards)."""
        return 5

    @inline
    def read_u16(self) -> uint16:
        """Alias for .value property (MicroPython compatibility)."""
        return self.value

    @inline
    def deinit(self):
        """Release the ADC resource (no-op on bare metal)."""
        pass

    @inline
    def __enter__(self):
        pass

    @inline
    def __exit__(self):
        self.deinit()


class AnalogOut:
    """AnalogOut is not supported on AVR (no DAC)."""
    @inline
    def __init__(self, pin_name):
        raise NotImplementedError("AnalogOut requires a DAC (not available on AVR)")

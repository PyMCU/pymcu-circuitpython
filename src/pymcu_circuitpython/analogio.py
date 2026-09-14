# CircuitPython-compatible analogio module for PyMCU
#
# Provides AnalogIn and AnalogOut, mirroring CircuitPython's analogio API.
#
# Usage (CircuitPython style):
#   from analogio import AnalogIn
#   import board
#
#   adc = AnalogIn(board.A0)
#   val = adc.value              # int, 0-65535, full scale on the pin reads 65535
#   vref = adc.reference_voltage # float volts, the reference the converter measures against
#   volts = val * vref / 65535
#
# Nothing here knows a converter's width, its reference or which pins have a channel
# behind them: pymcu.hal.adc answers all three, and refuses a pin it has no channel for
# where the AnalogIn is written.

from pymcu.types import uint16, inline
from pymcu.hal.adc import AnalogPin as _AnalogPin


class AnalogIn:
    @inline
    def __init__(self, pin):
        self._adc = _AnalogPin(pin)

    @property
    def value(self) -> uint16:
        """The pin's voltage as a 16-bit number, 0 to 65535, as CircuitPython reports it."""
        # read_u16 selects this pin's channel, converts and scales in one HAL call. The old
        # start() + read() pair started a conversion, threw it away and started another.
        return self._adc.read_u16()

    @property
    def reference_voltage(self) -> float:
        """The voltage the converter measures against, in volts.

        Comes from the HAL, which knows what each part's converter is wired to: the supply
        rail on the AVR and PIC parts, 3.3 V on the RP parts. It is a compile-time constant
        on every target, so the division that turns `value` into volts folds to a constant.
        """
        return self._adc.reference_volts()

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
    """A pin driven at an analog voltage by a digital-to-analog converter.

    The converter is the chip's, so a part that has none refuses the construction where it
    is written instead of building a program that drives nothing. On the AVR that refusal
    names pwmio.PWMOut, which with an RC filter on the pin is what an Arduino sketch means
    by analogWrite.
    """

    @inline
    def __init__(self, pin):
        from pymcu.hal.dac import DACPin as _DACPin
        self._value = 0
        self._dac = _DACPin(pin)

    @property
    def value(self) -> uint16:
        """The last value written, 0 to 65535. CircuitPython's AnalogOut.value is write-only
        in the sense that it reads back what was written, not the pin."""
        return self._value

    @value.setter
    def value(self, val: uint16):
        self._value = val
        self._dac.set_value_u16(val)

    @inline
    def deinit(self):
        self._dac.deinit()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

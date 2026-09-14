# CircuitPython-compatible pwmio module for PyMCU
#
# Provides PWMOut class that mirrors CircuitPython's pwmio.PWMOut API.
#
# Usage (CircuitPython style):
#   from pwmio import PWMOut
#   import board
#
#   pwm = PWMOut(board.D6, duty_cycle=32768)  # 50% duty cycle
#   pwm.duty_cycle = 49152                     # 75% duty cycle
#
# Note: CircuitPython's PWMOut.duty_cycle is 16-bit (0-65535), and so is the HAL's
#       duty_u16 / set_duty_u16 on every architecture; each chip's HAL resolves it
#       to its own compare register. Nothing here knows a chip's resolution.

from pymcu.chips import __CHIP__
from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, inline
if __CHIP__.arch == "avr":
    from pymcu.hal.pwm import PWM as _PWM


class PWMOut:
    # The first parameter is `pin`, as CircuitPython names it. It was `pin_name`, so the
    # keyword form every Adafruit guide uses -- PWMOut(pin=board.D9, ...) -- did not compile.
    @inline
    def __init__(self, pin, *, duty_cycle: uint16 = 0, frequency: uint16 = 500,
                 variable_frequency: uint8 = 0):
        self._duty_cycle_16   = duty_cycle
        self._frequency       = frequency
        self._variable_freq   = variable_frequency
        # The HAL constructor already programs the prescaler and connects the output:
        # a start() here wrote TCCRxB a second time and, since PyMCU#296, read the
        # compare register back to decide whether to reconnect (12 bytes per PWMOut).
        self._pwm = _PWM(pin, freq=frequency, duty_u16=duty_cycle)
        # What the pin actually emits, worked out here where the HAL's answer folds to a
        # constant. Read through `frequency` rather than recomputed, so that a driver holding
        # this PWMOut (adafruit_motor's Servo does) reads a field and not a call.
        self._real_frequency  = self._pwm.frequency()

    @property
    def duty_cycle(self) -> uint16:
        """Get duty cycle as 16-bit value (0-65535) to match CircuitPython."""
        return self._duty_cycle_16

    @duty_cycle.setter
    def duty_cycle(self, val: uint16):
        """Set duty cycle from 16-bit value (0-65535)."""
        self._duty_cycle_16 = val
        self._pwm.set_duty_u16(val)

    @property
    def frequency(self) -> uint16:
        """The frequency the pin actually emits, which is not always the one asked for.

        It used to report the request. On a timer whose period is fixed at 256 counts the
        frequencies on offer are a handful of buckets, so PWMOut(board.D6, frequency=5000)
        emits 7812 Hz and used to say 5000. The HAL answers with what it programmed.
        """
        return self._real_frequency

    @frequency.setter
    def frequency(self, val: uint16):
        """Set PWM frequency. CircuitPython allows it only on a PWMOut constructed with
        variable_frequency=True and raises otherwise; that construction argument is a
        compile-time constant here, so the refusal comes at compile time. The timer is
        reprogrammed to the nearest prescaler for the new frequency."""
        if self._variable_freq == 0:
            raise CompileError(
                "PWMOut.frequency is read-only: construct the PWMOut with "
                "variable_frequency=True to change the frequency after construction")
        self._frequency = val
        self._pwm.set_freq(val)
        self._real_frequency = self._pwm.frequency()

    @property
    def variable_frequency(self) -> uint8:
        """Returns 1 if variable_frequency was set at construction time."""
        return self._variable_freq

    @property
    def enabled(self) -> uint8:
        """PWM output is enabled after __init__ and until deinit()."""
        return 1

    @inline
    def deinit(self):
        """Stop PWM output and release the pin as an input, as CircuitPython does."""
        self._pwm.deinit()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

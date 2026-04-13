# CircuitPython-compatible pwmio module for Whipsnake
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
# Note: CircuitPython's PWMOut.duty_cycle is 16-bit (0-65535).
#       Whipsnake's PWM.set_duty() uses 8-bit (0-255) on AVR Timer0/Timer2.
#       We scale between the two representations.

from pymcu.types import uint8, uint16, inline
from pymcu.hal.pwm import PWM as _PWM


class PWMOut:
    @inline
    def __init__(self, pin_name, duty_cycle: uint16 = 0, frequency: uint16 = 0):
        # CircuitPython duty_cycle is 16-bit (0-65535)
        # Convert to 8-bit (0-255) for Whipsnake PWM
        duty8: uint8 = (duty_cycle >> 8) & 0xFF
        self._pwm = _PWM(pin_name, duty=duty8)
        self._pwm.start()
        # Note: frequency parameter is accepted for API compatibility
        # but AVR Timer0 Fast PWM frequency is fixed at F_CPU/256

    @property
    def duty_cycle(self) -> uint16:
        """Get duty cycle as 16-bit value (0-65535) to match CircuitPython."""
        # Whipsnake doesn't expose duty getter, so we track it internally
        return self._duty_cycle_16

    @duty_cycle.setter
    def duty_cycle(self, val: uint16):
        """Set duty cycle from 16-bit value (0-65535)."""
        self._duty_cycle_16 = val
        # Convert 16-bit to 8-bit by taking high byte
        duty8: uint8 = (val >> 8) & 0xFF
        self._pwm.set_duty(duty8)

    @inline
    def deinit(self):
        """Stop PWM output."""
        self._pwm.stop()

# adafruit_motor.servo for PyMCU
#
# The Adafruit servo driver, spelled as upstream spells it:
#
#   import board, pwmio
#   from adafruit_motor import servo
#
#   pwm = pwmio.PWMOut(board.D9, frequency=50)
#   s = servo.Servo(pwm)
#   s.angle = 90
#
# A servo reads the WIDTH of the pulse, not its duty cycle, so everything here is a pulse
# width in microseconds turned into a duty cycle against the PWM's actual period. That is
# why the frequency has to be the real one: a PWMOut that reported the frequency asked for
# rather than the one the pin emits put every angle in the wrong place.
#
# On the AVR, board.D9 and board.D10 at 50 Hz reach the timer mode whose period is a
# register, so the period is exactly 20 ms and one count is 0.5 us -- about 2000 steps
# across a servo's travel. Any other pin falls on one of the fixed frequency buckets, where
# 50 Hz becomes 61 Hz and the period has 256 counts of 64 us: a servo will still move, in
# about 16 steps, and its timing will be 22 % fast. Put the servo on D9 or D10.
#
# Differences from upstream, both because this compiles to firmware:
#
#   - The arithmetic is integer. Upstream computes the duty range in floating point; here
#     the same expression is evaluated in 32-bit integers, which on this part is both
#     faster and exact for every pulse width and frequency a servo uses.
#   - `angle` and `fraction` are read back from the last value written, as upstream does,
#     and `angle` is a whole number of degrees rather than a float.
#   - Import it as `from adafruit_motor.servo import Servo`. `from adafruit_motor import
#     servo`, which is what every guide writes, needs a submodule to be importable by name
#     and is refused (PyMCU#323).

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, int16, inline


class Servo:
    """A servo whose position is an angle.

    `actuation_range` is how many degrees the servo travels; `min_pulse` and `max_pulse` are
    the pulse widths in microseconds at the two ends. The defaults are upstream's, and they
    are wider than most hobby servos want: a servo that buzzes at the ends wants
    `min_pulse=1000, max_pulse=2000`.
    """

    @inline
    def __init__(self, pwm_out, actuation_range: uint16 = 180,
                 min_pulse: uint16 = 750, max_pulse: uint16 = 2250):
        self._pwm = pwm_out
        self._range: uint16 = actuation_range
        self._angle: uint16 = 0
        # The two ends of travel as duty cycles, worked out once at construction, which is
        # also where upstream works them out.
        #
        # The period, not the frequency, because the arithmetic has to stay inside a signed
        # 32-bit intermediate. Upstream writes duty = pulse * frequency / 1e6 * 0xFFFF, and
        # 1000 * 50 * 65535 is 3 276 750 000, past the top of int32; written that way with
        # literal operands the compiler refuses it outright. Against the period instead,
        # 1000 * 65535 is 65 535 000 and fits, and the answer is the same one.
        #
        # Every field here is annotated for the same kind of reason: an unannotated one takes
        # a width that is not the assigned value's, and 20000 came back as 32 with nothing
        # said. Measured on an Arduino Uno, that put a 689 us pulse on the pin where 1000 was
        # asked for (PyMCU#322).
        self._period: uint16 = uint16(1000000 // uint32(pwm_out.frequency))
        self._min_duty: uint16 = uint16(uint32(min_pulse) * 65535 // uint32(self._period))
        self._max_duty: uint16 = uint16(uint32(max_pulse) * 65535 // uint32(self._period))

    @inline
    def set_pulse_width_range(self, min_pulse: uint16 = 750, max_pulse: uint16 = 2250):
        """Change the pulse widths at the two ends of travel."""
        self._min_duty: uint16 = uint16(uint32(min_pulse) * 65535 // uint32(self._period))
        self._max_duty: uint16 = uint16(uint32(max_pulse) * 65535 // uint32(self._period))

    @property
    def angle(self) -> uint16:
        """The last angle written, in degrees."""
        return self._angle

    @angle.setter
    def angle(self, new_angle: uint16):
        if new_angle > self._range:
            raise CompileError(
                "this angle is past the end of the servo's travel. A Servo moves through "
                "actuation_range degrees, 180 by default; pass a larger actuation_range if "
                "the servo really does travel further, or ask for an angle inside it.")
        self._angle: uint16 = new_angle
        self._pwm.duty_cycle = uint16(
            uint32(self._min_duty)
            + uint32(self._max_duty - self._min_duty) * uint32(new_angle)
            // uint32(self._range))

    @property
    def fraction(self) -> uint16:
        """How far through its travel the servo was last sent, 0 to 65535."""
        return uint16(uint32(self._angle) * 65535 // uint32(self._range))

    @fraction.setter
    def fraction(self, value: uint16):
        """Send the servo a fraction of its travel, 0 to 65535.

        Upstream takes a float from 0.0 to 1.0. There are no floats in a parameter default
        here and soft-float on this part costs hundreds of cycles an operation, so the same
        range is spelled in the 16-bit fraction the rest of this layer uses for duty cycles.
        """
        self._angle: uint16 = uint16(uint32(value) * uint32(self._range) // 65535)
        self._pwm.duty_cycle = uint16(
            uint32(self._min_duty)
            + uint32(self._max_duty - self._min_duty) * uint32(value) // 65535)

    @inline
    def deinit(self):
        """Stop driving the servo and release the pin."""
        self._pwm.deinit()


class ContinuousServo:
    """A servo that turns continuously, whose control is a speed rather than a position.

    `throttle` runs from -32768 (full reverse) through 0 (stopped) to 32767 (full forward).
    Upstream takes a float from -1.0 to 1.0; the same range is spelled in whole numbers here
    for the same reason `Servo.fraction` is.
    """

    @inline
    def __init__(self, pwm_out, min_pulse: uint16 = 750, max_pulse: uint16 = 2250):
        self._pwm = pwm_out
        self._throttle: int16 = 0
        self._period: uint16 = uint16(1000000 // uint32(pwm_out.frequency))
        self._min_duty: uint16 = uint16(uint32(min_pulse) * 65535 // uint32(self._period))
        self._max_duty: uint16 = uint16(uint32(max_pulse) * 65535 // uint32(self._period))

    @property
    def throttle(self) -> int16:
        """The last speed written."""
        return self._throttle

    @throttle.setter
    def throttle(self, value: int16):
        self._throttle = value
        # -32768..32767 onto the two ends of travel, with 0 at the midpoint.
        self._pwm.duty_cycle = uint16(
            uint32(self._min_duty)
            + uint32(self._max_duty - self._min_duty) * uint32(value + 32768) // 65535)

    @inline
    def deinit(self):
        """Stop driving the servo and release the pin."""
        self._pwm.deinit()

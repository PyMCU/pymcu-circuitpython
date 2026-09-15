# CircuitPython-compatible rotaryio module for PyMCU
#
#   import board, rotaryio
#
#   knob = rotaryio.IncrementalEncoder(board.D2, board.D3)
#   last = knob.position
#   while True:
#       now = knob.position
#       if now != last:
#           print(now)
#           last = now
#
# Where a two-track knob has turned to. The two lines are a quarter turn out of phase, so
# which of them changed first says which way it went. Doing the decoding is
# pymcu.hal.encoder's business; this module is the CircuitPython shape around it.
#
# A common panel knob puts one click of detent every four changes, which is why `divisor`
# is 4 by default and why turning it one click moves `position` by one. A knob with a
# detent every other change takes divisor=2, and a continuous one takes divisor=1.

from pymcu.exceptions import CompileError
from pymcu.types import int32, uint8, inline, const
from pymcu.hal.encoder import Quadrature as _Quadrature


class IncrementalEncoder:
    """A two-track knob, counted in detents.

    One per program on the AVR: the position and the interrupts are module state in the HAL,
    so a second IncrementalEncoder would share them. Constructing two is not refused,
    because nothing at compile time can see the second construction as a second object.
    """

    @inline
    def __init__(self, pin_a, pin_b, divisor: const[uint8] = 4):
        if divisor != 1 and divisor != 2 and divisor != 4:
            raise CompileError(
                "a divisor is 1, 2 or 4. It is how many line changes the knob makes per "
                "detent, and a quadrature knob makes one, two or four of them; no other "
                "number describes a knob. Count the changes for one click of yours and pass "
                "that, or pass 1 and divide the position yourself.")
        self._q = _Quadrature(pin_a, pin_b, 1)
        self._divisor: uint8 = divisor

    @property
    def position(self) -> int32:
        """Where the knob is, in detents, counted from where it was when the program started.

        The HAL counts every line change, so the raw count is divided down. The division
        rounds towards zero, which keeps a knob turned one click back from where it started
        reading -1 and not -2.
        """
        raw: int32 = self._q.position()
        if self._divisor == 1:
            return raw
        if self._divisor == 2:
            if raw < 0:
                return -((-raw) >> 1)
            return raw >> 1
        if raw < 0:
            return -((-raw) >> 2)
        return raw >> 2

    @position.setter
    def position(self, value: int32):
        """Say where the knob is now. Everything after is counted from there."""
        if self._divisor == 1:
            self._q.set_position(value)
        elif self._divisor == 2:
            self._q.set_position(value + value)
        else:
            self._q.set_position(value + value + value + value)

    @property
    def divisor(self) -> uint8:
        """How many line changes make one detent."""
        return self._divisor

    @divisor.setter
    def divisor(self, value: uint8):
        raise CompileError(
            "the divisor is fixed when the encoder is built, because the position is divided "
            "by it with a shift and a shift needs its count known. Pass it to the "
            "constructor instead: rotaryio.IncrementalEncoder(pin_a, pin_b, divisor=2).")

    @inline
    def deinit(self):
        """Release the encoder. The interrupts stay attached: there are two pins behind them
        and nothing else can be decoding."""
        self._q.set_position(0)

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, *args):
        self.deinit()

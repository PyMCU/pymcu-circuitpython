# CircuitPython-compatible countio module for PyMCU
#
#   import board, countio
#
#   flow = countio.Counter(board.D2, edge=countio.Edge.FALL)
#   while True:
#       print(flow.count)
#       flow.reset()
#
# How many times a line changed: a flow meter, a tachometer, a wheel with one encoder track.
# What does the counting is pymcu.hal.counter's business, and on a part that cannot tell a
# rising edge from a falling one on the pin asked for, the ask is refused rather than
# counted twice.

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint32, inline, const
from pymcu.hal.counter import EdgeCounter as _EdgeCounter


class Edge:
    """Which edges to count.

    The numbers are the HAL's, so a value passed through needs no translation table.
    """
    RISE = 1
    FALL = 2
    RISE_AND_FALL = 0


class Counter:
    """How many edges have arrived on a pin.

    One per program on the AVR: the counter and the interrupt are module state in the HAL,
    so a second Counter would share them. Constructing two is not refused, because nothing
    at compile time can see the second construction as a second object.
    """

    @inline
    def __init__(self, pin, edge: const[uint8] = 2, pull=None):
        # CircuitPython's `pull` is a digitalio.Pull or None. The pull-up is on unless the
        # program says otherwise, because the thing being counted is usually a switch or an
        # open-collector sensor pulling the line down; `pull=None` leaves the pin floating,
        # which is what an already-driven signal wants.
        match pull:
            case None:
                self._counter = _EdgeCounter(pin, edge, 1)
            case _:
                self._counter = _EdgeCounter(pin, edge, pull)

    @property
    def count(self) -> uint32:
        """How many edges have arrived since the last reset."""
        return self._counter.count()

    @count.setter
    def count(self, value: uint32):
        """CircuitPython allows `counter.count = 0` to clear it, and nothing else."""
        if value != 0:
            raise CompileError(
                "a counter can only be set to zero: it counts edges as they arrive and there "
                "is nowhere to start it from. Use counter.reset(), or counter.count = 0, "
                "and keep your own offset if you need one.")
        self._counter.reset()

    @inline
    def reset(self):
        """Set the count back to zero."""
        self._counter.reset()

    @inline
    def deinit(self):
        """Release the counter. The interrupt stays attached: there is one pin behind it and
        nothing else can be counting."""
        self._counter.reset()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, *args):
        self.deinit()

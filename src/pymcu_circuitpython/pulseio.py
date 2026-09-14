# CircuitPython-compatible pulseio module for PyMCU
#
# PulseIn measures the pulses arriving on a pin; PulseOut sends a gated carrier. Between
# them they are how an infrared remote, an HC-SR04 rangefinder and a DHT temperature sensor
# are read and driven in CircuitPython.
#
#   import board, pulseio
#
#   pulses = pulseio.PulseIn(board.D2, maxlen=68, idle_state=True)
#   while len(pulses) < 68:
#       pass
#   first = pulses[0]            # microseconds
#   pulses.clear()
#
#   out = pulseio.PulseOut(board.D3, frequency=38000, duty_cycle=32768)
#   out.send(frame)              # microseconds, carrier on for the first
#
# Nothing here knows a timer, a prescaler or a vector: pymcu.hal.pulse answers all of it,
# and refuses where the chip cannot do what was asked.

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, inline, const
from pymcu.hal.pulse import PulseCapture as _PulseCapture, PulseTrain as _PulseTrain


class PulseIn:
    """The lengths of the pulses arriving on a pin, in microseconds, oldest first.

    One per program on the AVR: the buffer and the edge timestamp are module state in the
    HAL and there is no per-instance storage to give a second one. Constructing two is not
    refused, because nothing at compile time can see the second construction as a second
    object; they would share one buffer.
    """

    @inline
    def __init__(self, pin, maxlen: const[uint16] = 2, idle_state: const[uint8] = 0):
        self._cap = _PulseCapture(pin, maxlen, idle_state)

    @inline
    def __len__(self) -> uint16:
        """How many pulses are waiting. `len(pulses)`, as CircuitPython spells it."""
        return self._cap.count()

    @inline
    def __getitem__(self, index: uint16) -> uint16:
        """The index-th oldest pulse, left in the buffer. Out of range reads as 0."""
        return self._cap.get(index)

    @inline
    def popleft(self) -> uint16:
        """Remove and return the oldest pulse."""
        return self._cap.popleft()

    @property
    def maxlen(self) -> uint16:
        """How many pulses this PulseIn will hold."""
        return self._cap.maxlen()

    @inline
    def clear(self):
        """Throw away every pulse held, and start the next one from the next edge."""
        self._cap.clear()

    @inline
    def pause(self):
        """Stop recording. Pulses that arrive while paused are lost, not queued."""
        self._cap.pause()

    @inline
    def resume(self, trigger_duration: uint16 = 0):
        """Start recording again.

        CircuitPython's `trigger_duration` sends a pulse on the pin first, to trigger a
        sensor that answers on the same line. This pin is an input while it is being
        measured, so there is nothing here to drive: a non-zero duration is refused rather
        than accepted and dropped. Drive the trigger with a digitalio.DigitalInOut on the
        pin before constructing the PulseIn, which is what a DHT driver does.
        """
        if trigger_duration != 0:
            raise CompileError(
                "pulseio.PulseIn.resume() cannot send a trigger pulse: the pin is an input "
                "while it is being measured and this HAL does not turn it round. Drive the "
                "trigger yourself with a digitalio.DigitalInOut on the pin, then construct "
                "or resume the PulseIn. Call resume() with no argument for the rest.")
        self._cap.resume()

    @property
    def paused(self) -> uint8:
        """1 while recording is stopped."""
        return self._cap.paused()

    @inline
    def deinit(self):
        """Stop recording and release the pin."""
        self._cap.deinit()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()


class PulseOut:
    """A gated carrier on a pin: what an infrared emitter sends.

    `send(pulses)` walks the durations in microseconds with the carrier on for the first,
    off for the second, and so on, which is CircuitPython's convention. The pin is fixed by
    the timer channel the carrier comes out of, and a pin that has no channel is refused
    where the PulseOut is written.
    """

    @inline
    def __init__(self, pin, frequency: const[uint32] = 38000,
                 duty_cycle: const[uint16] = 32768):
        self._train = _PulseTrain(pin, frequency, duty_cycle)

    @inline
    def send(self, pulses, count: uint16):
        """Send `count` durations from `pulses`, carrier on for the first.

        CircuitPython spells this `send(pulses)` and takes the length from the array. A
        module-level array loses its length and its iterability when it crosses a parameter
        (PyMCU#258), so neither `len(pulses)` nor `for p in pulses` can work here and the
        count is asked for instead. When that lands, `count` becomes optional and nothing
        else in this module changes.
        """
        self._train.send(pulses, count)

    @inline
    def deinit(self):
        """Stop the carrier and release the pin."""
        self._train.deinit()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

# circuitpython_typing.io for PyMCU
#
# Mirrors the upstream module (adafruit/Adafruit_CircuitPython_Typing):
# Protocol classes that name value-like IO objects. Upstream they exist for
# static checkers only; here they must be real scanned classes so a
# Union[ROValueIO, ...] parameter can match a DigitalInOut argument
# structurally -- the Protocol base registers by name and the compiler checks
# that the argument's class carries every member the protocol declares.

from typing import Protocol


class ROValueIO(Protocol):
    # Hardware objects, like analogio.AnalogIn, that have read-only
    # `value` properties/attributes.

    @property
    def value(self) -> float:
        # Value property, that may return an int or float depending
        # on the specifics of the class.
        return 0.0


class ValueIO(Protocol):
    # Hardware objects, like analogio.AnalogOut, that have read and
    # write `value` properties/attributes.

    @property
    def value(self) -> float:
        # Value property, that may return an int or float depending
        # on the specifics of the class.
        return 0.0

    @value.setter
    def value(self, input_value: float) -> None:
        pass

# circuitpython_typing.pwmio for PyMCU
#
# Mirrors the upstream submodule (adafruit/Adafruit_CircuitPython_Typing):
# drivers import it guarded, `from circuitpython_typing import pwmio`, and put
# `pwmio.PWMOut` inside Union[...] parameters (adafruit_character_lcd's RGB
# pins). Upstream it exists for static checkers only; here it must be a real
# scanned class so the parameter can match an argument structurally -- the
# Protocol base registers by name and the compiler checks that the argument's
# class carries every member the protocol declares, so the real pwmio.PWMOut
# and any compatible object both satisfy it.

from typing import Protocol


class PWMOut(Protocol):
    # Protocol that implements, at the bare minimum, the `duty_cycle` property.

    @property
    def duty_cycle(self) -> int:
        # The duty cycle as a ratio using 16-bits.
        return 0

    @duty_cycle.setter
    def duty_cycle(self, duty_cycle: int) -> None:
        pass

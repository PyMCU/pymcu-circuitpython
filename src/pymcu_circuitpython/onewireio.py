# onewireio for PyMCU
#
# Mirrors the upstream module: a 1-Wire master on a single GPIO, bit-banged
# open-drain. CircuitPython timing:
#   reset   -- drive low 480us, release, sample at ~70us (low = a device
#              answered with a presence pulse), wait out the slot.
#   write 0 -- hold low ~60us; write 1 -- hold low ~6us then release.
#   read    -- pull low ~3us, release, sample at ~12us, wait out the slot.
# reset() returns True when the bus stayed HIGH (no presence pulse) -- the
# polarity adafruit_onewire expects: `if required and reset: raise "No
# presence pulse found"`.

from pymcu.types import uint8, inline
from pymcu.time import delay_us
from digitalio import DigitalInOut, Pull


class OneWire:
    @inline
    def __init__(self, pin) -> None:
        self._io = DigitalInOut(pin)
        self._io.switch_to_input(pull=Pull.UP)

    @inline
    def _low(self):
        self._io.switch_to_output(value=False)

    @inline
    def _release(self):
        self._io.switch_to_input(pull=Pull.UP)

    def reset(self) -> bool:
        self._low()
        delay_us(480)
        self._release()
        delay_us(70)
        absent = self._io.value
        delay_us(410)
        return absent != 0

    def read_bit(self) -> bool:
        self._low()
        delay_us(3)
        self._release()
        delay_us(9)
        bit = self._io.value
        delay_us(55)
        return bit != 0

    def write_bit(self, value: uint8) -> None:
        self._low()
        if value:
            delay_us(6)
            self._release()
            delay_us(64)
        else:
            delay_us(60)
            self._release()
            delay_us(10)

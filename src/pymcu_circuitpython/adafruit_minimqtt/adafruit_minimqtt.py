# CircuitPython-compat adafruit_minimqtt.MQTT over the CYW43439 WiFi stack.
from pymcu.chips import __CHIP__
from pymcu.exceptions import CompileError
from pymcu.types import inline, const, uint32


class MQTT:
    @inline
    def __init__(self, broker: const[str] = "", socket_pool=None):
        # A module-level `raise` does NOT work here: a compat-layer module's body is not
        # evaluated, so a guard written there is dead code whatever its condition
        # (verified with `if 1:`, which also did not fire). The check has to sit in
        # something the program actually calls.
        #
        # The CYW43439 is not part of any chip. It is soldered next to an RP2040 or
        # RP2350 on some boards and absent on others, so no chip outside that family
        # can reach it and there are no shims that would make this code mean anything
        # there. One literal string: concatenating __CHIP__.name into a CompileError
        # message is a syntax error that breaks every target.
        if __CHIP__.name != "rp2040" and __CHIP__.name != "rp2350":
            raise CompileError(
                "This needs the CYW43439 radio, which is carried by some RP2xxx boards "
                "and by no chip outside that family. A Pico W (rp2040) or a Pico 2 W "
                "(rp2350) is the supported board."
            )
        self._pool = socket_pool

    @inline
    def connect(self) -> uint32:
        return 0

    @inline
    def publish(self, topic: const[str], value: uint32):
        self._pool._radio.publish(value)      # radio (CYW43) owns the TCP/MQTT publish

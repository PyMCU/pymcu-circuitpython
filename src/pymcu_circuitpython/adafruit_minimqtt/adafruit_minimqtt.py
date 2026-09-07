# CircuitPython-compat adafruit_minimqtt.MQTT over the CYW43439 WiFi stack.
from pymcu.types import inline, const, uint32


class MQTT:
    @inline
    def __init__(self, broker: const[str] = "", socket_pool=None):
        self._pool = socket_pool

    @inline
    def connect(self) -> uint32:
        return 0

    @inline
    def publish(self, topic: const[str], value: uint32):
        self._pool._radio.publish(value)      # radio (CYW43) owns the TCP/MQTT publish

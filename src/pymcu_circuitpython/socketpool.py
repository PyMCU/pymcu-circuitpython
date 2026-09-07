# CircuitPython-compat socketpool (minimal): carries the radio to the MQTT client.
from pymcu.types import inline


class SocketPool:
    @inline
    def __init__(self, radio):
        self._radio = radio

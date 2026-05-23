# CircuitPython-compatible digitalio module for PyMCU
#
# Provides DigitalInOut, Direction, and Pull as ZCA (zero-cost) classes that
# mirror the CircuitPython digitalio API.
#
# Usage (CircuitPython style):
#   from digitalio import DigitalInOut, Direction, Pull
#   import board
#
#   led = DigitalInOut(board.LED)
#   led.direction = Direction.OUTPUT   # property setter
#   led.value = 1                      # property setter
#
# ZCA contract:
#   - Direction.OUTPUT / Direction.INPUT are compile-time integer constants.
#   - Assigning to .direction / .value expands the property setter inline,
#     enabling dead-code elimination in any method that matches on self.direction.
#   - set_direction() / set_value() / get_value() are kept as explicit helpers
#     for code that prefers the call style.

from pymcu.types import uint8, inline
from pymcu.hal.gpio import Pin as _Pin


class Direction:
    INPUT  = 0
    OUTPUT = 1


class Pull:
    NONE = 0
    UP   = 1
    DOWN = 2


class DriveMode:
    """Drive mode for digital outputs."""
    PUSH_PULL  = 0   # Standard push-pull output (default)
    OPEN_DRAIN = 1   # Open-drain output (requires external pull-up)


class DigitalInOut:
    @inline
    def __init__(self, pin_name):
        self._pin        = _Pin(pin_name, _Pin.IN)
        # Store backing field directly — avoids triggering the setter which
        # would call _pin.mode(IN) redundantly (_Pin.__init__ already sets IN).
        self._direction  = Direction.INPUT
        self._pull_mode  = Pull.NONE
        self._drive_mode = DriveMode.PUSH_PULL

    # ------------------------------------------------------------------
    # direction property
    # ------------------------------------------------------------------

    @property
    def direction(self) -> uint8:
        return self._direction

    @direction.setter
    def direction(self, d: uint8):
        self._direction = d
        match d:
            case Direction.OUTPUT:
                self._pin.mode(_Pin.OUT)
            case Direction.INPUT:
                self._pin.mode(_Pin.IN)

    # ------------------------------------------------------------------
    # value property
    # ------------------------------------------------------------------

    @property
    def value(self) -> uint8:
        return self._pin.value()

    @value.setter
    def value(self, val: uint8):
        match val:
            case 0:
                self._pin.low()
            case _:
                self._pin.high()

    # ------------------------------------------------------------------
    # pull property
    # ------------------------------------------------------------------

    @property
    def pull(self) -> uint8:
        return self._pull_mode

    @pull.setter
    def pull(self, p: uint8):
        self._pull_mode = p
        self._pin.pull(p)

    # ------------------------------------------------------------------
    # drive_mode property
    # ------------------------------------------------------------------

    @property
    def drive_mode(self) -> uint8:
        return self._drive_mode

    @drive_mode.setter
    def drive_mode(self, mode: uint8):
        self._drive_mode = mode
        match mode:
            case DriveMode.OPEN_DRAIN:
                # Open-drain: set pin to INPUT when high, OUTPUT+LOW when low
                # This requires application logic; for now we just store the mode
                self._pin.mode(_Pin.OPEN_DRAIN)
            case DriveMode.PUSH_PULL:
                self._pin.mode(_Pin.OUT)

    # ------------------------------------------------------------------
    # switch_to helpers (CircuitPython API)
    # ------------------------------------------------------------------

    @inline
    def switch_to_output(self, value: uint8 = 0, drive_mode: uint8 = DriveMode.PUSH_PULL):
        """Configure pin as output with optional initial value and drive mode."""
        self._direction  = Direction.OUTPUT
        self._drive_mode = drive_mode
        self._pin.mode(_Pin.OUT)
        match value:
            case 0:
                self._pin.low()
            case _:
                self._pin.high()

    @inline
    def switch_to_input(self, pull: uint8 = Pull.NONE):
        """Configure pin as input with optional pull resistor."""
        self._direction = Direction.INPUT
        self._pull_mode = pull
        self._pin.mode(_Pin.IN)
        self._pin.pull(pull)

    # ------------------------------------------------------------------
    # deinit / context manager (CircuitPython API)
    # ------------------------------------------------------------------

    @inline
    def deinit(self):
        """Release the pin resource (sets pin back to input, no pull)."""
        self._pin.mode(_Pin.IN)
        self._pull_mode  = Pull.NONE
        self._drive_mode = DriveMode.PUSH_PULL
        self._direction  = Direction.INPUT

    @inline
    def __enter__(self):
        pass

    @inline
    def __exit__(self):
        self.deinit()

    # ------------------------------------------------------------------
    # Explicit call-style helpers (kept for backwards compatibility)
    # ------------------------------------------------------------------

    @inline
    def set_direction(self, d: uint8):
        self.direction = d

    @inline
    def set_pull(self, p: uint8):
        self.pull = p

    @inline
    def get_value(self) -> uint8:
        return self._pin.value()

    @inline
    def set_value(self, val: uint8):
        match val:
            case 0:
                self._pin.low()
            case _:
                self._pin.high()

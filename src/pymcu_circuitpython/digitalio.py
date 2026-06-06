# CircuitPython-compatible digitalio module for PyMCU
#
# Provides DigitalInOut, Direction, Pull and DriveMode as ZCA (zero-cost)
# classes that mirror the CircuitPython digitalio API exactly.
#
# Usage (CircuitPython style):
#   from digitalio import DigitalInOut, Direction, Pull
#   import board
#
#   led = DigitalInOut(board.LED)
#   led.direction = Direction.OUTPUT   # property setter
#   led.value = True                   # property setter
#
#   btn = DigitalInOut(board.D2)
#   btn.switch_to_input(pull=Pull.UP)
#   if btn.value:
#       ...
#
# ZCA contract:
#   - Direction.OUTPUT / Direction.INPUT and Pull.UP / Pull.DOWN are compile-time
#     integer constants; "no pull" is the Python value None (folds to -1).
#   - Assigning to .direction / .value expands the property setter inline,
#     enabling dead-code elimination in any method that matches on it.
#
# Note: pin-change interrupts are a PyMCU feature, not part of CircuitPython's
#       digitalio API. Use pymcu.hal.gpio.Pin(...).irq(...) directly for them.

from pymcu.types import uint8, inline
from pymcu.hal.gpio import Pin as _Pin


class Direction:
    INPUT  = 0
    OUTPUT = 1


class Pull:
    # CircuitPython's Pull has only UP and DOWN; "no pull" is None (not a member).
    UP   = 1
    DOWN = 2


class DriveMode:
    """Drive mode for digital outputs."""
    PUSH_PULL  = 0   # Standard push-pull output (default)
    OPEN_DRAIN = 1   # Open-drain output (requires external pull-up)


class DigitalInOut:
    @inline
    def __init__(self, pin):
        self._pin        = _Pin(pin, _Pin.IN)
        # Store backing fields directly -- avoids triggering the setters which
        # would call _pin.mode(IN) redundantly (_Pin.__init__ already sets IN).
        self._direction  = Direction.INPUT
        self._pull_mode  = None
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
    def pull(self):
        return self._pull_mode

    @pull.setter
    def pull(self, p):
        self._pull_mode = p
        match p:
            case Pull.UP:
                self._pin.pull(1)
            case Pull.DOWN:
                # AVR has no internal pull-down; the HAL raises a CompileError
                # so the deviation is reported at build time rather than ignored.
                self._pin.pull(2)
            case _:
                # None / no pull.
                self._pin.pull(0)

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
    def switch_to_input(self, pull=None):
        """Configure pin as input with optional pull resistor (Pull.UP or None)."""
        self._direction = Direction.INPUT
        self._pin.mode(_Pin.IN)
        self.pull = pull

    # ------------------------------------------------------------------
    # deinit / context manager (CircuitPython API)
    # ------------------------------------------------------------------

    @inline
    def deinit(self):
        """Release the pin resource (sets pin back to input, no pull)."""
        self._pin.mode(_Pin.IN)
        self._pull_mode  = None
        self._drive_mode = DriveMode.PUSH_PULL
        self._direction  = Direction.INPUT

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

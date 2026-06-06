"""digitalio: DigitalInOut, Direction, Pull (UP/DOWN, None = no pull), DriveMode."""
from pymcu_circuitpython.digitalio import DigitalInOut, Direction, Pull, DriveMode


def test_direction_constants():
    assert Direction.INPUT == 0
    assert Direction.OUTPUT == 1


def test_pull_constants_no_none():
    assert Pull.UP == 1
    assert Pull.DOWN == 2
    assert not hasattr(Pull, "NONE")   # CircuitPython uses None, not Pull.NONE


def test_drive_mode_constants():
    assert DriveMode.PUSH_PULL == 0
    assert DriveMode.OPEN_DRAIN == 1


def test_default_is_input_no_pull():
    d = DigitalInOut("PB5")
    assert d.direction == Direction.INPUT
    assert d.pull is None


def test_direction_setter():
    d = DigitalInOut("PB5")
    d.direction = Direction.OUTPUT
    assert d.direction == Direction.OUTPUT


def test_value_setter_getter():
    d = DigitalInOut("PB5")
    d.direction = Direction.OUTPUT
    d.value = True
    assert d.value == 1
    d.value = False
    assert d.value == 0


def test_pull_none_and_up():
    d = DigitalInOut("PB5")
    d.switch_to_input(pull=Pull.UP)
    assert d.pull == Pull.UP
    d.pull = None
    assert d.pull is None


def test_switch_to_output_initial_value():
    d = DigitalInOut("PB5")
    d.switch_to_output(value=1)
    assert d.direction == Direction.OUTPUT
    assert d.value == 1


def test_no_legacy_helpers():
    # Strict CircuitPython parity: the old call-style helpers are gone.
    for attr in ("toggle", "set_value", "get_value", "set_direction", "set_pull", "irq"):
        assert not hasattr(DigitalInOut, attr)


def test_context_manager():
    with DigitalInOut("PB5") as d:
        d.direction = Direction.OUTPUT

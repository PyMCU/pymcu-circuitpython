from pymcu_circuitpython.digitalio import Direction, DriveMode, Pull, DigitalInOut


def test_direction_constants():
    assert Direction.INPUT == 0
    assert Direction.OUTPUT == 1


def test_pull_constants():
    assert Pull.NONE == 0
    assert Pull.UP == 1
    assert Pull.DOWN == 2


def test_drive_mode_constants():
    assert DriveMode.PUSH_PULL == 0
    assert DriveMode.OPEN_DRAIN == 1


def test_digital_in_out_default_state():
    pin = DigitalInOut("PB5")
    assert pin.direction == Direction.INPUT
    assert pin.pull == Pull.NONE
    assert pin.drive_mode == DriveMode.PUSH_PULL


def test_digital_in_out_set_output():
    pin = DigitalInOut("PB5")
    pin.direction = Direction.OUTPUT
    assert pin.direction == Direction.OUTPUT


def test_digital_in_out_set_input():
    pin = DigitalInOut("PB5")
    pin.direction = Direction.OUTPUT
    pin.direction = Direction.INPUT
    assert pin.direction == Direction.INPUT


def test_digital_in_out_set_pull():
    pin = DigitalInOut("PB5")
    pin.pull = Pull.UP
    assert pin.pull == Pull.UP
    pin.pull = Pull.DOWN
    assert pin.pull == Pull.DOWN


def test_digital_in_out_drive_mode():
    pin = DigitalInOut("PB5")
    pin.drive_mode = DriveMode.OPEN_DRAIN
    assert pin.drive_mode == DriveMode.OPEN_DRAIN
    pin.drive_mode = DriveMode.PUSH_PULL
    assert pin.drive_mode == DriveMode.PUSH_PULL


def test_digital_in_out_value_read():
    pin = DigitalInOut("PB5")
    v = pin.value
    assert v == 0


def test_digital_in_out_value_write():
    pin = DigitalInOut("PB5")
    pin.direction = Direction.OUTPUT
    pin.value = 1
    pin.value = 0  # should not raise


def test_digital_in_out_helper_set_direction():
    pin = DigitalInOut("PB5")
    pin.set_direction(Direction.OUTPUT)
    assert pin.direction == Direction.OUTPUT


def test_digital_in_out_helper_set_pull():
    pin = DigitalInOut("PB5")
    pin.set_pull(Pull.UP)
    assert pin.pull == Pull.UP


def test_digital_in_out_helper_get_set_value():
    pin = DigitalInOut("PB5")
    assert pin.get_value() == 0
    pin.set_value(1)  # should not raise
    pin.set_value(0)  # should not raise

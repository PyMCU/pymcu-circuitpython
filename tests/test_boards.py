from pymcu_circuitpython.boards import arduino_uno, arduino_nano
from pymcu_circuitpython.board_chips import BOARD_CHIPS


# ── Arduino Uno digital pins ──────────────────────────────────────────────  #

def test_arduino_uno_digital_pins():
    assert arduino_uno.D0  == "PD0"
    assert arduino_uno.D1  == "PD1"
    assert arduino_uno.D2  == "PD2"
    assert arduino_uno.D3  == "PD3"
    assert arduino_uno.D4  == "PD4"
    assert arduino_uno.D5  == "PD5"
    assert arduino_uno.D6  == "PD6"
    assert arduino_uno.D7  == "PD7"
    assert arduino_uno.D8  == "PB0"
    assert arduino_uno.D9  == "PB1"
    assert arduino_uno.D10 == "PB2"
    assert arduino_uno.D11 == "PB3"
    assert arduino_uno.D12 == "PB4"
    assert arduino_uno.D13 == "PB5"


def test_arduino_uno_analog_pins():
    assert arduino_uno.A0 == "PC0"
    assert arduino_uno.A1 == "PC1"
    assert arduino_uno.A2 == "PC2"
    assert arduino_uno.A3 == "PC3"
    assert arduino_uno.A4 == "PC4"
    assert arduino_uno.A5 == "PC5"


def test_arduino_uno_named_pins():
    assert arduino_uno.LED         == "PB5"
    assert arduino_uno.LED_BUILTIN == "PB5"
    assert arduino_uno.TX   == "PD1"
    assert arduino_uno.RX   == "PD0"
    assert arduino_uno.SCL  == "PC5"
    assert arduino_uno.SDA  == "PC4"
    assert arduino_uno.SCK  == "PB5"
    assert arduino_uno.MOSI == "PB3"
    assert arduino_uno.MISO == "PB4"
    assert arduino_uno.SS   == "PB2"


# ── Arduino Nano ─────────────────────────────────────────────────────────  #

def test_arduino_nano_led():
    assert arduino_nano.LED == "PB5"
    assert arduino_nano.LED_BUILTIN == "PB5"


def test_arduino_nano_digital_pins():
    assert arduino_nano.D0  == "PD0"
    assert arduino_nano.D13 == "PB5"


def test_arduino_nano_analog_pins():
    assert arduino_nano.A0 == "PC0"
    assert arduino_nano.A5 == "PC5"


def test_arduino_nano_named_pins():
    assert arduino_nano.TX  == "PD1"
    assert arduino_nano.RX  == "PD0"
    assert arduino_nano.SCL == "PC5"
    assert arduino_nano.SDA == "PC4"


# ── board_chips ──────────────────────────────────────────────────────────  #

def test_board_chips_is_dict():
    assert isinstance(BOARD_CHIPS, dict)


def test_board_chips_empty_for_cp():
    # All standard AVR Arduino boards are already in the build driver's mapping.
    # The CP extension dict is intentionally empty until CP-specific boards
    # (e.g., Adafruit Metro) with fully working codegen are added.
    assert len(BOARD_CHIPS) == 0

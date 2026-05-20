from pymcu_circuitpython.boards import (
    arduino_uno, arduino_nano, arduino_mega, arduino_micro,
    digispark, attiny85, attiny45, attiny25, attiny84, attiny44, attiny24,
    attiny2313, attiny4313, attiny13, attiny13a,
)
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


def test_board_chips_attiny_named_boards():
    assert BOARD_CHIPS["digispark"]        == "attiny85"
    assert BOARD_CHIPS["adafruit_trinket"] == "attiny85"


def test_board_chips_attiny85_family():
    assert BOARD_CHIPS["attiny85"] == "attiny85"
    assert BOARD_CHIPS["attiny45"] == "attiny45"
    assert BOARD_CHIPS["attiny25"] == "attiny25"


def test_board_chips_attiny84_family():
    assert BOARD_CHIPS["attiny84"] == "attiny84"
    assert BOARD_CHIPS["attiny44"] == "attiny44"
    assert BOARD_CHIPS["attiny24"] == "attiny24"


def test_board_chips_attiny2313_family():
    assert BOARD_CHIPS["attiny2313"] == "attiny2313"
    assert BOARD_CHIPS["attiny4313"] == "attiny4313"


def test_board_chips_attiny13_family():
    assert BOARD_CHIPS["attiny13"]  == "attiny13"
    assert BOARD_CHIPS["attiny13a"] == "attiny13a"


# ── Arduino Mega 2560 ─────────────────────────────────────────────────────  #

def test_arduino_mega_digital_pins():
    assert arduino_mega.D0  == "PE0"
    assert arduino_mega.D1  == "PE1"
    assert arduino_mega.D13 == "PB7"
    assert arduino_mega.D22 == "PA0"
    assert arduino_mega.D53 == "PB0"


def test_arduino_mega_analog_pins():
    assert arduino_mega.A0  == "PF0"
    assert arduino_mega.A7  == "PF7"
    assert arduino_mega.A8  == "PK0"
    assert arduino_mega.A15 == "PK7"


def test_arduino_mega_named_pins():
    assert arduino_mega.LED         == "PB7"
    assert arduino_mega.LED_BUILTIN == "PB7"
    assert arduino_mega.TX   == "PE1"
    assert arduino_mega.RX   == "PE0"
    assert arduino_mega.SCL  == "PD0"
    assert arduino_mega.SDA  == "PD1"
    assert arduino_mega.SCK  == "PB1"
    assert arduino_mega.MOSI == "PB2"
    assert arduino_mega.MISO == "PB3"
    assert arduino_mega.SS   == "PB0"


# ── Arduino Micro ─────────────────────────────────────────────────────────  #

def test_arduino_micro_digital_pins():
    assert arduino_micro.D0  == "PD2"
    assert arduino_micro.D1  == "PD3"
    assert arduino_micro.D13 == "PC7"


def test_arduino_micro_analog_pins():
    assert arduino_micro.A0 == "PF7"
    assert arduino_micro.A5 == "PF0"


def test_arduino_micro_named_pins():
    assert arduino_micro.LED         == "PC7"
    assert arduino_micro.LED_BUILTIN == "PC7"
    assert arduino_micro.TX  == "PD3"
    assert arduino_micro.RX  == "PD2"
    assert arduino_micro.SCL == "PD0"
    assert arduino_micro.SDA == "PD1"


# ── Digispark ─────────────────────────────────────────────────────────────  #

def test_digispark_pins():
    assert digispark.P0 == "PB0"
    assert digispark.P1 == "PB1"
    assert digispark.P2 == "PB2"
    assert digispark.P3 == "PB3"
    assert digispark.P4 == "PB4"
    assert digispark.P5 == "PB5"


def test_digispark_led():
    assert digispark.LED         == "PB1"
    assert digispark.LED_BUILTIN == "PB1"


def test_digispark_analog():
    assert digispark.A1 == "PB2"
    assert digispark.A2 == "PB4"


# ── ATtiny85 ──────────────────────────────────────────────────────────────  #

def test_attiny85_pins():
    assert attiny85.PB0 == "PB0"
    assert attiny85.PB1 == "PB1"
    assert attiny85.PB2 == "PB2"
    assert attiny85.PB5 == "PB5"
    assert attiny85.A1  == "PB2"
    assert attiny85.SCL == "PB2"
    assert attiny85.SDA == "PB0"


def test_attiny45_pins():
    assert attiny45.PB0 == "PB0"
    assert attiny45.A1  == "PB2"


def test_attiny25_pins():
    assert attiny25.PB0 == "PB0"
    assert attiny25.A1  == "PB2"


# ── ATtiny84 ──────────────────────────────────────────────────────────────  #

def test_attiny84_pins():
    assert attiny84.D0  == "PA0"
    assert attiny84.D7  == "PA7"
    assert attiny84.D8  == "PB0"
    assert attiny84.D10 == "PB2"
    assert attiny84.A0  == "PA0"
    assert attiny84.A7  == "PA7"
    assert attiny84.SCK == "PB2"


def test_attiny44_pins():
    assert attiny44.D0 == "PA0"
    assert attiny44.D8 == "PB0"


def test_attiny24_pins():
    assert attiny24.D0 == "PA0"
    assert attiny24.D8 == "PB0"


# ── ATtiny2313 ────────────────────────────────────────────────────────────  #

def test_attiny2313_pins():
    assert attiny2313.D0  == "PD0"
    assert attiny2313.D6  == "PD6"
    assert attiny2313.D7  == "PB0"
    assert attiny2313.D14 == "PB7"
    assert attiny2313.TX  == "PD1"
    assert attiny2313.RX  == "PD0"
    assert attiny2313.SCL == "PB2"


def test_attiny4313_pins():
    assert attiny4313.D0  == "PD0"
    assert attiny4313.D14 == "PB7"
    assert attiny4313.TX  == "PD1"


# ── ATtiny13 ──────────────────────────────────────────────────────────────  #

def test_attiny13_pins():
    assert attiny13.PB0  == "PB0"
    assert attiny13.PB5  == "PB5"
    assert attiny13.A1   == "PB2"
    assert attiny13.INT0 == "PB1"


def test_attiny13a_pins():
    assert attiny13a.PB0  == "PB0"
    assert attiny13a.INT0 == "PB1"

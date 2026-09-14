# CircuitPython-style board pin constants for Arduino Nano (ATmega328P @ 16 MHz)
#
# The Arduino Nano uses the same ATmega328P chip as the Arduino Uno, with identical
# pin mappings. This file is provided for CircuitPython compatibility when users
# specify board = "arduino_nano" in their pyproject.toml.
#
# Usage (after build driver generates dist/_generated/board.py):
#   import board
#   led = DigitalInOut(board.LED)
#
# Pin mapping is identical to Arduino Uno:
#   board.LED / board.LED_BUILTIN -> PB5 (D13)
#   board.D0 .. board.D13, board.A0 .. board.A5
#   board.SCL -> A5   board.SDA -> A4
#   board.TX  -> D1   board.RX  -> D0
#   board.SCK -> D13  board.MOSI -> D11  board.MISO -> D12  board.SS -> D10

# Digital pins (D0-D13)
D0  = "PD0"
D1  = "PD1"
D2  = "PD2"
D3  = "PD3"
D4  = "PD4"
D5  = "PD5"
D6  = "PD6"
D7  = "PD7"
D8  = "PB0"
D9  = "PB1"
D10 = "PB2"
D11 = "PB3"
D12 = "PB4"
D13 = "PB5"

# Analog pins (A0-A5)
A0 = "PC0"
A1 = "PC1"
A2 = "PC2"
A3 = "PC3"
A4 = "PC4"
A5 = "PC5"
# Nano-specific ADC-only pins (no GPIO port connection)
A6 = "ADC6"
A7 = "ADC7"

# CircuitPython canonical aliases
LED         = "PB5"   # Built-in LED (D13)
LED_BUILTIN = "PB5"
TX   = "PD1"   # UART TX (D1)
RX   = "PD0"   # UART RX (D0)
SCL  = "PC5"   # I2C Clock (A5)
SDA  = "PC4"   # I2C Data (A4)
SCK  = "PB5"   # SPI Clock (D13)
MOSI = "PB3"   # SPI MOSI (D11)
MISO = "PB4"   # SPI MISO (D12)
SS   = "PB2"   # SPI SS (D10)


# The three bus constructors every Adafruit guide opens with: `i2c = board.I2C()` is the
# first line of nearly every sensor example, and they did not exist here at all.
#
# They are functions and not module-level objects because a bus must only be built when the
# program asks for one: a module-level `i2c = busio.I2C(SCL, SDA)` would program the TWI in
# every program that imports board.
#
# They take no arguments, as CircuitPython's do: board.UART() is the board's default UART,
# 9600 8N1. It leaves the receive ring off, where busio.UART turns it on by default, because
# an uncalled function that registers an ISR still plants it: a buffered UART here cost every
# program that imports board the 118 bytes of the receive interrupt whether or not it ever
# built one. For another rate, or for the buffer that makes in_waiting a count, construct
# busio.UART(board.TX, board.RX, ...) directly.
#
# The aliases are _board_* and not _I2C/_SPI/_UART because an import alias is not scoped to
# its module in the compiler's flattening: busio already aliases the HAL classes to those
# names, and a second module using them makes each class construct itself, reported as a
# recursive __init__ in a file the change never touched (PyMCU#320).
#
# These were written, measured and reverted once. Adding them made a program that imports
# both board and busio lose its UART parity -- 7E2 came out 7N2, silently -- which turned out
# to be a keyword argument dropped when the same @inline is called twice with the parameter
# at its default (PyMCU#324, fixed). They are back on the fixed compiler.
from busio import I2C as _board_i2c, SPI as _board_spi, UART as _board_uart


def I2C():
    return _board_i2c(SCL, SDA)


def SPI():
    return _board_spi(SCK, MOSI, MISO)


def UART():
    return _board_uart(TX, RX, baudrate=9600, receiver_buffer_size=1)

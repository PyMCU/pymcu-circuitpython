# CircuitPython-style board pin constants for Arduino Micro (ATmega32U4 @ 16 MHz)
#
# Pin mapping follows the official Arduino Micro silk-screen numbering.
# Digital D0-D13, Analog A0-A5, plus CircuitPython canonical aliases.
#
# Note: explicit string literals are required here because the PyMCU compiler only
# registers module-level globals for explicit assignments, not re-exported imports.

# Digital pins
D0  = "PD2"   # RX  / INT2
D1  = "PD3"   # TX  / INT3
D2  = "PD1"   # SDA / INT1
D3  = "PD0"   # SCL / INT0 / OC0B
D4  = "PD4"   # ADC8 / ICP1
D5  = "PC6"   # OC3A / #OC4A
D6  = "PD7"   # OC4D / ADC10 / T0
D7  = "PE6"   # INT6 / AIN0
D8  = "PB4"   # PCINT4 / ADC11
D9  = "PB5"   # PCINT5 / OC1A / #OC4B / ADC12
D10 = "PB6"   # PCINT6 / OC1B / OC4B / ADC13
D11 = "PB7"   # PCINT7 / OC0A / OC1C / #RTS
D12 = "PD6"   # T1 / #OC4D / ADC9
D13 = "PC7"   # ICP3 / CLK0 / OC4A / LED

# Analog pins (Port F, ADC channels in reverse order on Micro)
A0 = "PF7"   # ADC7
A1 = "PF6"   # ADC6
A2 = "PF5"   # ADC5
A3 = "PF4"   # ADC4
A4 = "PF1"   # ADC1
A5 = "PF0"   # ADC0

# CircuitPython canonical aliases
LED         = "PC7"   # D13 built-in LED
LED_BUILTIN = "PC7"
TX   = "PD3"   # D1  / USART1 TX
RX   = "PD2"   # D0  / USART1 RX
SCL  = "PD0"   # D3  / TWI SCL
SDA  = "PD1"   # D2  / TWI SDA
SCK  = "PB1"   # ICSP SCK  / PCINT1
MOSI = "PB2"   # ICSP MOSI / PCINT2
MISO = "PB3"   # ICSP MISO / PCINT3
SS   = "PB0"   # ICSP SS   / PCINT0


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

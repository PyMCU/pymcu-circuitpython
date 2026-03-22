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

# CircuitPython board pin constants for the Adafruit Feather RP2040 (RP2040 @ 125 MHz)
#
# Pin names and GPIO numbers come from the CircuitPython board definition:
#   https://github.com/adafruit/circuitpython/blob/main/ports/raspberrypi/boards/adafruit_feather_rp2040/pins.c
# Default bus pins come from the same directory's mpconfigboard.h.
#
# Only the names that pins.c exports are defined here. Pins the board does not
# expose under a CircuitPython name (D2, D3, D7, D8, D14-D23) are absent on purpose.
#
# Usage:
#   import board
#   from digitalio import DigitalInOut, Direction
#   from busio import UART
#
#   led = DigitalInOut(board.LED)
#   led.direction = Direction.OUTPUT
#   uart = UART(board.TX, board.RX, baudrate=115200)

# Analog pins
A0 = 26
A1 = 27
A2 = 28
A3 = 29

# Digital pins (CircuitPython D-names)
D0  = 1
D1  = 0
D4  = 6
D5  = 7
D6  = 8
D9  = 9
D10 = 10
D11 = 11
D12 = 12
D13 = 13
D24 = 24
D25 = 25

# Named pins
LED      = 13   # GP13 -- onboard LED (same pin as D13)
BUTTON   = 4    # GP4  -- user button
BOOT     = 4    # GP4  -- same pin as BUTTON
NEOPIXEL = 16   # GP16 -- onboard NeoPixel

TX   = 0    # GP0  -- UART0 TX (same pin as D1)
RX   = 1    # GP1  -- UART0 RX (same pin as D0)

SCL  = 3    # GP3  -- I2C1 SCL (default)
SDA  = 2    # GP2  -- I2C1 SDA (default)

SCK  = 18   # GP18 -- SPI0 SCK (default)
MOSI = 19   # GP19 -- SPI MOSI (default, mpconfigboard.h)
MISO = 20   # GP20 -- SPI MISO (default, mpconfigboard.h)


# The three bus constructors every Adafruit guide opens with: `i2c = board.I2C()`
# is the first line of nearly every sensor example (see raspberry_pi_pico.py for
# the full rationale -- functions, not module-level objects).
#
# receiver_buffer_size=1 on UART(): same reasoning as raspberry_pi_pico.py -- the
# RP2040 UART receive buffer is the PL011 hardware FIFO, so the receive size must
# stay within 32 entries.
from busio import I2C as _board_i2c, SPI as _board_spi, UART as _board_uart


def I2C():
    return _board_i2c(SCL, SDA)


def SPI():
    return _board_spi(SCK, MOSI, MISO)


def UART():
    return _board_uart(TX, RX, baudrate=9600, receiver_buffer_size=1)

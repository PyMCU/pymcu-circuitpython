# CircuitPython board pin constants for Raspberry Pi Pico (RP2040 @ 125 MHz)
#
# Pin identifiers are integer GP numbers (0-29), matching the SIO bit index
# used by the RP2040 HAL.  The standard Pico pinout is used throughout.
#
# Usage:
#   import board
#   from digitalio import DigitalInOut, Direction
#   from busio import UART
#
#   led = DigitalInOut(board.LED)
#   led.direction = Direction.OUTPUT
#   uart = UART(board.TX, board.RX, baudrate=115200)

# General-purpose I/O -- all 30 pins
GP0  = 0
GP1  = 1
GP2  = 2
GP3  = 3
GP4  = 4
GP5  = 5
GP6  = 6
GP7  = 7
GP8  = 8
GP9  = 9
GP10 = 10
GP11 = 11
GP12 = 12
GP13 = 13
GP14 = 14
GP15 = 15
GP16 = 16
GP17 = 17
GP18 = 18
GP19 = 19
GP20 = 20
GP21 = 21
GP22 = 22
GP25 = 25
GP26 = 26
GP27 = 27
GP28 = 28

# CircuitPython canonical aliases
LED  = 25   # GP25 -- onboard LED on standard Pico

TX   = 0    # GP0  -- UART0 TX
RX   = 1    # GP1  -- UART0 RX

SCL  = 5    # GP5  -- I2C0 SCL (Pico default)
SDA  = 4    # GP4  -- I2C0 SDA (Pico default)

SCK  = 18   # GP18 -- SPI0 SCK (Pico default)
MOSI = 19   # GP19 -- SPI0 TX  (Pico default)
MISO = 16   # GP16 -- SPI0 RX  (Pico default)


# The three bus constructors every Adafruit guide opens with: `i2c = board.I2C()`
# is the first line of nearly every sensor example (see arduino_uno.py's own
# copy of this comment for the full rationale -- functions, not module-level
# objects, so a program that never calls board.I2C() never pays to build one).
#
# receiver_buffer_size=1 on UART(): the RP2040/RP2350 UART HAL's receive
# buffer is the PL011's own 32-entry hardware FIFO, not an interrupt-driven
# ring like AVR's -- busio.UART refuses a receiver_buffer_size over 32, and
# the board default (64) is already past that. 1 keeps board.UART() a
# single-byte-polled UART with no ring at all, exactly as it is on AVR.
from busio import I2C as _board_i2c, SPI as _board_spi, UART as _board_uart


def I2C():
    return _board_i2c(SCL, SDA)


def SPI():
    return _board_spi(SCK, MOSI, MISO)


def UART():
    return _board_uart(TX, RX, baudrate=9600, receiver_buffer_size=1)

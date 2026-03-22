# UART Echo -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.TX / board.RX / board.LED resolved at compile time
#   busio module  -- UART serial read/write
#   digitalio     -- LED OUTPUT, blinks on each received byte
#
# Adapted from Adafruit CircuitPython Essentials UART Serial example
# Original: Copyright (c) 2018 Kattni Rembor, Adafruit Industries (MIT)
#
# Changes from the original CircuitPython code:
#   - Property syntax (led.direction, led.value) -> set_direction() / set_value()
#   - uart.read(32)   -> uart.read()  (single-byte blocking; no bytearrays on AVR)
#   - ''.join([chr(b) for b in data]) -> uart.write(byte)  (no list comprehension)
#   - data is not None -> removed  (blocking read always returns a byte)
#   - Added def main() wrapper required by pymcu entry convention
#
# Wiring:
#   LED:    built-in on D13 (no external wiring needed)
#   Serial: connect USB-to-serial adapter to TX (D1) / RX (D0) at 9600 baud
#
import board
import busio
from digitalio import DigitalInOut, Direction
from whipsnake.types import uint8


def main():
    led = DigitalInOut(board.LED)
    led.set_direction(Direction.OUTPUT)

    uart = busio.UART(board.TX, board.RX, baudrate=9600)

    while True:
        byte: uint8 = uart.read()
        led.set_value(1)
        uart.write(byte)
        led.set_value(0)

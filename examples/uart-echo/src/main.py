# UART Echo -- CircuitPython style on Arduino Uno
#
# Reads one byte and echoes it back, blinking the LED on each byte.
# Adapted from the Adafruit CircuitPython Essentials UART example.
#
# Minimal change from desktop CircuitPython: a bytearray(1) receive buffer is
# declared as a fixed-size `uint8[1]` (PyMCU has no heap), and uart.readinto()
# fills it -- the standard CircuitPython in-place read API.
#
import board
import busio
from digitalio import DigitalInOut, Direction
from pymcu.types import uint8


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    uart = busio.UART(board.TX, board.RX, baudrate=9600)
    buf: uint8[1]

    while True:
        uart.readinto(buf)
        led.value = True
        uart.write(buf)
        led.value = False

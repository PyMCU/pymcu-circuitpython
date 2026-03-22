# CircuitPython-compatible busio module for Whipsnake
#
# Provides a minimal UART class that mirrors CircuitPython's busio.UART API.
# On ATmega328P the TX/RX pins are fixed (PD1 / PD0), so the tx and rx board
# constants are accepted for API compatibility but are not used for pin setup.
#
# Usage:
#   import busio
#   import board
#   uart = busio.UART(board.TX, board.RX, baudrate=9600)
#   uart.println("Hello")
#   uart.print_byte(value)

from whipsnake.types import uint8, uint16, inline, const
from whipsnake.hal.uart import UART as _UART


class UART:
    @inline
    def __init__(self, tx, rx, baudrate: uint16 = 9600):
        # tx/rx accepted for API compatibility; hardware pins are fixed on
        # ATmega328P (PD1=TX, PD0=RX) and configured inside _UART.__init__.
        self._hw = _UART(baudrate)

    @inline
    def write(self, data: uint8):
        self._hw.write(data)

    @inline
    def write_str(self, s: const[str]):
        self._hw.write_str(s)

    @inline
    def println(self, s: const[str]):
        self._hw.println(s)

    @inline
    def print_byte(self, value: uint8):
        self._hw.print_byte(value)

    @inline
    def read(self) -> uint8:
        return self._hw.read()

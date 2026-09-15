# expect: build
# source: CircuitPython busio UART echo using readinto buffer
import board
import busio

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)
buf = bytearray(1)

while True:
    n = uart.readinto(buf)
    if n:
        uart.write(buf)

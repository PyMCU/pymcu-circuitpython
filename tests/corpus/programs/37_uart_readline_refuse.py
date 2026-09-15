# expect: refuse busio.UART.readline() returns a bytes object
# source: CircuitPython busio UART readline docs style
import board
import busio

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)

while True:
    line = uart.readline()
    if line:
        print(line)

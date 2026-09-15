# expect: build
# source: CircuitPython busio UART constructor frame format docs style
import time
import board
import busio

uart = busio.UART(board.TX, board.RX, baudrate=19200, bits=7, parity=busio.Parity.EVEN, stop=1)

while True:
    uart.write(b"ready\r\n")
    time.sleep(1)

# expect: refuse busio.UART.read() returns a bytes object
# source: CircuitPython busio UART docs read/write echo shape
import board
import busio

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)

while True:
    data = uart.read(32)
    if data is not None:
        uart.write(data)

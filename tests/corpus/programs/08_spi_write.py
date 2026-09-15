# expect: refuse bytearray() is a Python builtin that PyMCU does not provide
# source: CircuitPython busio SPI write example shape
import time
import board
import busio
import digitalio

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D10)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

while True:
    cs.value = False
    spi.write(bytearray([0x9F, 0x00]))
    cs.value = True
    time.sleep(1)

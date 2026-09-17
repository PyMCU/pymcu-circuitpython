# expect: build
# source: CircuitPython bitbangio SPI docs shape
import time
import board
import bitbangio

spi = bitbangio.SPI(board.D5, MOSI=board.D6, MISO=board.D7)

while True:
    spi.write(bytearray([0x55, 0xAA]))
    time.sleep(1)

# expect: build
# source: CircuitPython busio SPI write_readinto register transaction style
import time
import board
import busio

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
out_buf = bytearray([0x00, 0x00])
in_buf = bytearray(2)

while True:
    spi.write_readinto(out_buf, in_buf)
    print(in_buf[0], in_buf[1])
    time.sleep(1)

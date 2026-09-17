# expect: build
# source: CircuitPython bitbangio I2C docs shape
import time
import board
import bitbangio

i2c = bitbangio.I2C(board.D3, board.D4, frequency=100000)
buf = bytearray(1)

while True:
    i2c.writeto_then_readfrom(0x40, bytearray([0xF3]), buf)
    print(buf[0])
    time.sleep(1)

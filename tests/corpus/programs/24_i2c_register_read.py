# expect: build
# source: CircuitPython busio I2C writeto_then_readfrom sensor register style
import time
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
result = bytearray(2)

while True:
    i2c.writeto_then_readfrom(0x48, bytearray([0x00]), result)
    print(result[0], result[1])
    time.sleep(1)

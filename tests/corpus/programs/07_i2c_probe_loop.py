# expect: build
# source: CircuitPython busio I2C shape adapted to fixed-address sensor probe
import time
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

while True:
    if i2c.try_lock():
        if i2c.probe(0x68):
            print("found", 0x68)
        i2c.unlock()
    time.sleep(1)

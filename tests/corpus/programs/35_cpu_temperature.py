# expect: build
# source: CircuitPython microcontroller.cpu temperature docs style
import time
import microcontroller

while True:
    print(microcontroller.cpu.temperature)
    time.sleep(1)

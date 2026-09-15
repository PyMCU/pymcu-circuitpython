# expect: build
# source: CircuitPython microcontroller.nvm byte storage docs style
import time
import microcontroller

count = microcontroller.nvm[0]
count = (count + 1) & 0xFF
microcontroller.nvm[0] = count

while True:
    print(count)
    time.sleep(1)

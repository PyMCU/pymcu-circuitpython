# expect: build
# source: CircuitPython countio Counter docs edge counting style
import time
import board
import countio

counter = countio.Counter(board.D2, edge=countio.Edge.RISE)

while True:
    print(counter.count)
    time.sleep(1)

# expect: refuse an encoder's two lines have to be on the same port
# source: CircuitPython rotaryio IncrementalEncoder docs with common pin-pair shape
import time
import board
import rotaryio

encoder = rotaryio.IncrementalEncoder(board.D2, board.D8)

while True:
    print(encoder.position)
    time.sleep(0.1)

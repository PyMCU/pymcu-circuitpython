# expect: build
# source: CircuitPython rotaryio IncrementalEncoder docs style
import time
import board
import rotaryio

encoder = rotaryio.IncrementalEncoder(board.D2, board.D3)
last_position = None

while True:
    position = encoder.position
    if last_position is None or position != last_position:
        print(position)
    last_position = position
    time.sleep(0.01)

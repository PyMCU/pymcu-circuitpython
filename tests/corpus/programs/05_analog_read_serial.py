# expect: build
# source: Adafruit Learn CircuitPython Essentials analog input print loop style
import time
import board
from analogio import AnalogIn

analog_in = AnalogIn(board.A0)

while True:
    print(analog_in.value)
    time.sleep(0.1)

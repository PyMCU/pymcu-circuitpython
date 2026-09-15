# expect: build
# source: Adafruit Learn analog input voltage helper style
import time
import board
from analogio import AnalogIn

analog_in = AnalogIn(board.A0)

while True:
    volts = analog_in.value * analog_in.reference_voltage / 65535
    print((volts,))
    time.sleep(0.5)

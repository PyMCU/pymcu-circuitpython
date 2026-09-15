# expect: refuse this chip has no digital-to-analog converter
# source: CircuitPython analogio AnalogOut docs DAC output style
import time
import board
from analogio import AnalogOut

dac = AnalogOut(board.A0)

while True:
    dac.value = 32768
    time.sleep(1)

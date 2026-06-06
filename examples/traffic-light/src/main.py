# Traffic Light -- CircuitPython style on Arduino Uno
#
# Three independent OUTPUT pins (ZCA, zero SRAM overhead).
# Wiring: D11 red, D12 yellow, D13 green (each + 220 ohm to GND).
#
import board
import time
from digitalio import DigitalInOut, Direction


def main():
    red    = DigitalInOut(board.D11)
    yellow = DigitalInOut(board.D12)
    green  = DigitalInOut(board.D13)

    red.direction    = Direction.OUTPUT
    yellow.direction = Direction.OUTPUT
    green.direction  = Direction.OUTPUT

    while True:
        red.value = True;  yellow.value = False; green.value = False
        time.sleep(3.0)
        red.value = True;  yellow.value = True;  green.value = False
        time.sleep(0.5)
        red.value = False; yellow.value = False; green.value = True
        time.sleep(3.0)
        red.value = False; yellow.value = True;  green.value = False
        time.sleep(1.0)

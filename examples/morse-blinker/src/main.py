# Morse Blinker (SOS) -- CircuitPython style on Arduino Uno
#
# dot()/dash() are @inline so the ZCA DigitalInOut can be passed to them.
# Timing: 1 dit = 200 ms.
#
import board
import time
from digitalio import DigitalInOut, Direction
from pymcu.types import inline


@inline
def dot(led):
    led.value = True
    time.sleep(0.2)
    led.value = False
    time.sleep(0.2)


@inline
def dash(led):
    led.value = True
    time.sleep(0.6)
    led.value = False
    time.sleep(0.2)


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    while True:
        dot(led); dot(led); dot(led)
        time.sleep(0.4)    # letter gap
        dash(led); dash(led); dash(led)
        time.sleep(0.4)    # letter gap
        dot(led); dot(led); dot(led)
        time.sleep(1.2)    # word gap

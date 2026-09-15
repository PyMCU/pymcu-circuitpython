# expect: build
# source: Adafruit HCSR04 library docs distance loop shape, expressed with pulseio
import time
import board
from digitalio import DigitalInOut, Direction
from pulseio import PulseIn

trigger = DigitalInOut(board.D5)
trigger.direction = Direction.OUTPUT
echo = PulseIn(board.D2, maxlen=2)
echo.pause()
echo.clear()

while True:
    echo.clear()
    trigger.value = True
    time.sleep(0.00001)
    trigger.value = False
    echo.resume()
    while len(echo) == 0:
        pass
    echo.pause()
    print((echo[0] * 0.017,))
    time.sleep(0.1)

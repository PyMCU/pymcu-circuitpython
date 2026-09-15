# expect: refuse call to undefined function 'w_feed'
# source: CircuitPython watchdog module docs feed loop style
import time
import microcontroller
from watchdog import WatchDogMode

w = microcontroller.watchdog
w.timeout = 2
w.mode = WatchDogMode.RESET

while True:
    w.feed()
    time.sleep(0.5)

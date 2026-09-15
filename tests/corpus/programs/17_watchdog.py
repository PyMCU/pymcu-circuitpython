# expect: build
# source: CircuitPython watchdog module docs feed loop style
# note: used to be refused ("call to undefined function 'w_feed'"); watchdog.feed() now
# resolves and arms/feeds correctly. Verified in avr8sharp: MCUSR stays 0 (no reset) over
# 6s of simulated time with timeout=2 fed every 0.5s.
import time
import microcontroller
from watchdog import WatchDogMode

w = microcontroller.watchdog
w.timeout = 2
w.mode = WatchDogMode.RESET

while True:
    w.feed()
    time.sleep(0.5)

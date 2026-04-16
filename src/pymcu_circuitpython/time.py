# CircuitPython-compatible time module for PyMCU
#
# Provides sleep(), sleep_ms(), and sleep_us() that map directly to
# the underlying PyMCU delay functions (no runtime overhead).
#
# Usage:
#   import time
#   time.sleep(1)          # 1 second
#   time.sleep_ms(500)     # 500 ms
#   time.sleep_us(100)     # 100 us

from pymcu.types import uint8, uint16, inline
from pymcu.time import delay_ms, delay_us


@inline
def sleep(seconds: uint16):
    # CircuitPython's sleep() takes a float; on MCUs we use integer seconds.
    delay_ms(seconds * 1000)


@inline
def sleep_ms(ms: uint16):
    delay_ms(ms)


@inline
def sleep_us(us: uint8):
    delay_us(us)

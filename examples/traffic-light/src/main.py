# Traffic Light -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.D11, board.D12, board.D13 resolved at compile time
#   digitalio     -- three independent OUTPUT pins (ZCA, zero SRAM overhead)
#   time module   -- sleep_ms() for phase timing
#
# Wiring:
#   D11 (PB3) -- Red    LED + 220 ohm resistor to GND
#   D12 (PB4) -- Yellow LED + 220 ohm resistor to GND
#   D13 (PB5) -- Green  LED (built-in, or external)
#
# State machine:
#   Red (3 s) -> Red+Yellow (500 ms) -> Green (3 s) -> Yellow (1 s) -> repeat
#
import board
import time
from digitalio import DigitalInOut, Direction


def main():
    red    = DigitalInOut(board.D11)
    yellow = DigitalInOut(board.D12)
    green  = DigitalInOut(board.D13)

    red.set_direction(Direction.OUTPUT)
    yellow.set_direction(Direction.OUTPUT)
    green.set_direction(Direction.OUTPUT)

    while True:
        # --- Red phase (stop) ---
        red.set_value(1)
        yellow.set_value(0)
        green.set_value(0)
        time.sleep_ms(3000)

        # --- Red + Yellow (prepare to go) ---
        red.set_value(1)
        yellow.set_value(1)
        green.set_value(0)
        time.sleep_ms(500)

        # --- Green phase (go) ---
        red.set_value(0)
        yellow.set_value(0)
        green.set_value(1)
        time.sleep_ms(3000)

        # --- Yellow (slow down) ---
        red.set_value(0)
        yellow.set_value(1)
        green.set_value(0)
        time.sleep_ms(1000)

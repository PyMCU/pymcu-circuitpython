# expect: build
# source: Adafruit Learn CircuitPython Essentials PWM fade style
import time
import board
import pwmio

led = pwmio.PWMOut(board.D9, frequency=5000, duty_cycle=0)

while True:
    for i in range(100):
        led.duty_cycle = i * 655
        time.sleep(0.01)
    for i in range(100, 0, -1):
        led.duty_cycle = i * 655
        time.sleep(0.01)

# expect: refuse a PWM running at an exact frequency cannot be retuned at run time
# source: CircuitPython pwmio PWMOut variable frequency property style
import time
import board
import pwmio

buzzer = pwmio.PWMOut(board.D9, duty_cycle=32768, frequency=440, variable_frequency=True)

while True:
    buzzer.frequency = 440
    time.sleep(0.2)
    buzzer.frequency = 880
    time.sleep(0.2)

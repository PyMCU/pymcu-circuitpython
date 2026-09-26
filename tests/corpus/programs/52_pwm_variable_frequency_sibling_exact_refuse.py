# expect: refuse Timer1 period (PB1 and PB2 share ICR1)
# source: CircuitPython pwmio PWMOut variable frequency property style, second channel on the same timer
# D9 and D10 are Timer1's two channels and share its period register. Retuning D9 at run time
# while D10 also runs at an exact frequency would change D10's frequency and duty cycle, which
# CircuitPython never does to a second PWMOut, so it is refused and the refusal names the pins.
import time
import board
import pwmio

buzzer = pwmio.PWMOut(board.D9, duty_cycle=32768, frequency=440, variable_frequency=True)
other = pwmio.PWMOut(board.D10, duty_cycle=16384, frequency=440)

while True:
    buzzer.frequency = 880
    time.sleep(0.2)
    buzzer.frequency = 440
    time.sleep(0.2)

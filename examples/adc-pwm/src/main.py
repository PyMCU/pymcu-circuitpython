# ADC-controlled PWM dimming -- CircuitPython style on Arduino Uno
#
#   analogio.AnalogIn (A0)  -> pwmio.PWMOut duty cycle (D6 / OC0A)
#
# Wiring: potentiometer wiper -> A0; LED + resistor -> D6.
#
import board
from analogio import AnalogIn
from pwmio import PWMOut
from time import sleep


def main():
    pot = AnalogIn(board.A0)
    led = PWMOut(board.D6, duty_cycle=0)

    while True:
        led.duty_cycle = pot.value   # both are 16-bit (0-65535)
        sleep(0.01)

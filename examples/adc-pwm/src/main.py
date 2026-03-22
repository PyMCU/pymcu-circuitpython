# ADC-controlled PWM dimming (CircuitPython style)
#
# Demonstrates:
#   - analogio.AnalogIn for reading ADC values
#   - pwmio.PWMOut for PWM output control
#   - board module for pin names
#   - Property-based API (led.duty_cycle = value)
#
# Circuit:
#   - Potentiometer: A0 (wiper) → GND/VCC for variable input
#   - LED: D6 (OC0A) with 220Ω resistor → GND
#
# Behavior:
#   - Reads ADC value from A0 (0-65535)
#   - Sets LED brightness via PWM duty cycle (0-65535)
#   - Updates continuously in loop

import board
from analogio import AnalogIn
from pwmio import PWMOut
from time import sleep_ms


def main():
    # Initialize ADC on A0
    pot = AnalogIn(board.A0)

    # Initialize PWM on D6 (OC0A, Timer0)
    led = PWMOut(board.D6, duty_cycle=0)

    while True:
        # Read potentiometer (0-65535)
        adc_value = pot.value

        # Set LED brightness directly from ADC value
        led.duty_cycle = adc_value

        # Small delay to avoid flickering
        sleep_ms(10)

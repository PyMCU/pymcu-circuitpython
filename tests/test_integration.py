"""Cross-module smoke: the common CircuitPython idioms used together."""
from pymcu_circuitpython.digitalio import DigitalInOut, Direction, Pull
from pymcu_circuitpython.busio import UART
from pymcu_circuitpython.analogio import AnalogIn
from pymcu_circuitpython.pwmio import PWMOut


def test_gpio_uart_adc_pwm_together():
    led = DigitalInOut("PB5")
    led.direction = Direction.OUTPUT
    led.value = True

    btn = DigitalInOut("PD2")
    btn.switch_to_input(pull=Pull.UP)
    _ = btn.value

    uart = UART(None, None, baudrate=9600)
    uart.write(b"hi")

    adc = AnalogIn("PC0")
    pwm = PWMOut("PD6", duty_cycle=0)
    pwm.duty_cycle = adc.value & 0xFFFF

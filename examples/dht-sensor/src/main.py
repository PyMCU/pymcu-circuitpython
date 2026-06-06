# DHT11 Sensor -- CircuitPython style on Arduino Uno
#
# Reads a DHT11 and reports over UART. Status text is sent as bytes literals;
# the humidity/temperature values are sent as raw bytes (PyMCU has no runtime
# integer-to-decimal formatting, so the host decodes the two value bytes).
#
# Wiring: DHT11 DATA -> D2 (4.7k pull-up to +5V); LED on D13; TX on D1 @ 9600.
#
import board
import time
import busio
from digitalio import DigitalInOut, Direction
from dht11 import DHT11
from pymcu.types import uint8


def main():
    uart   = busio.UART(board.TX, board.RX, baudrate=9600)
    led    = DigitalInOut(board.LED)
    sensor = DHT11(board.D2)

    led.direction = Direction.OUTPUT
    uart.write(b"DHT11 ready\r\n")

    val: uint8[1]
    while True:
        sensor.measure()

        if sensor.failed:
            uart.write(b"read error\r\n")
            led.value = False
        else:
            uart.write(b"H:")
            val[0] = sensor.humidity
            uart.write(val)
            uart.write(b" T:")
            val[0] = sensor.temperature
            uart.write(val)
            uart.write(b"\r\n")
            led.value = True
            time.sleep(0.1)
            led.value = False

        time.sleep(2.0)

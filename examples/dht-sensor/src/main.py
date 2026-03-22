# DHT11 Sensor -- CircuitPython style on Arduino Uno
#
# Demonstrates:
#   board module  -- board.D2 for sensor data, board.LED for status
#   busio module  -- UART serial output (board.TX / board.RX, 9600 baud)
#   digitalio     -- LED OUTPUT, blinks on each successful read
#   time module   -- sleep_ms() between measurements
#   local driver  -- dht11.DHT11 reads temperature & humidity
#
# Wiring:
#   DHT11 DATA -> D2 (with 4.7 kohm pull-up to +5 V)
#   DHT11 VCC  -> +5 V
#   DHT11 GND  -> GND
#   LED:    built-in on D13 (no wiring needed)
#   Serial: connect USB-to-serial adapter to TX (D1) at 9600 baud
#
# UART output format:
#   Startup:  "DHT11 ready"
#   OK read:  "H: XX  T: XX"   (humidity %, temperature C)
#   Error:    "read error"
#
import board
import time
import busio
from digitalio import DigitalInOut, Direction
from dht11 import DHT11


def main():
    uart   = busio.UART(board.TX, board.RX, baudrate=9600)
    led    = DigitalInOut(board.LED)
    sensor = DHT11(board.D2)

    led.set_direction(Direction.OUTPUT)

    uart.println("DHT11 ready")

    while True:
        sensor.measure()

        if sensor.failed:
            uart.println("read error")
            led.set_value(0)
        else:
            uart.write_str("H: ")
            uart.print_byte(sensor.humidity)
            uart.write_str("T: ")
            uart.print_byte(sensor.temperature)
            led.set_value(1)
            time.sleep_ms(100)
            led.set_value(0)

        time.sleep_ms(2000)

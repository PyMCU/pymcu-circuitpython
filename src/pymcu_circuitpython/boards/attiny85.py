# CircuitPython-style board pin constants for ATtiny85 bare chip (8-pin DIP)
# Also pin-compatible with ATtiny45 and ATtiny25 (same package, less flash/SRAM).
#
# PB0-PB5 only (PORTB). PB5 = RESET by default.
# No hardware UART. SPI/I2C use USI (bit-bang) on PB0/PB2.

# Port B pins
PB0 = "PB0"   # MOSI / SDA / OC1A / PCINT0 / DI
PB1 = "PB1"   # MISO / OC0B / OC1A / AIN0 / PCINT1 / DO
PB2 = "PB2"   # SCK  / SCL  / ADC1 / INT0  / USCK / PCINT2
PB3 = "PB3"   # ADC3 / AIN1 / PCINT3
PB4 = "PB4"   # ADC2 / PCINT4
PB5 = "PB5"   # ADC0 / RESET / dW / PCINT5 -- GPIO requires RSTDISBL fuse!

# Analog channels
A0 = "PB5"   # ADC0 -- requires RSTDISBL fuse
A1 = "PB2"   # ADC1
A2 = "PB4"   # ADC2
A3 = "PB3"   # ADC3

# Named aliases (no LED on bare chip)
SCK  = "PB2"   # USI USCK
MOSI = "PB0"   # USI MOSI / DI
MISO = "PB1"   # USI MISO / DO
SCL  = "PB2"   # USI SCL (same as SCK)
SDA  = "PB0"   # USI SDA (same as MOSI)
INT0 = "PB2"   # External interrupt 0

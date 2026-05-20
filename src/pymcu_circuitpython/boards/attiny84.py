# CircuitPython-style board pin constants for ATtiny84 bare chip (14-pin DIP)
# Also pin-compatible with ATtiny44 (4KB flash) and ATtiny24 (2KB flash).
#
# Port A: PA0-PA7 (8 digital/analog pins)
# Port B: PB0-PB3 (4 pins; PB3 = RESET by default)
# No hardware UART. SPI/I2C use USI on PB0-PB2.
# ADC on PA0-PA7 (8 channels, ADC0-ADC7).

# Port A -- digital and analog
D0  = "PA0"   # ADC0 / PCINT0
D1  = "PA1"   # ADC1 / AIN0 / PCINT1
D2  = "PA2"   # ADC2 / AIN1 / PCINT2
D3  = "PA3"   # ADC3 / T0   / PCINT3
D4  = "PA4"   # ADC4 / SCL  / USCK / PCINT4
D5  = "PA5"   # ADC5 / MISO / DO   / OC1B / PCINT5
D6  = "PA6"   # ADC6 / MOSI / SDA  / DI  / OC1A / PCINT6
D7  = "PA7"   # ADC7 / OC0B / PCINT7

# Port B -- digital
D8  = "PB0"   # MOSI / DI  / SDA / OC1B / PCINT8   (ATtinyCore D8)
D9  = "PB1"   # MISO / DO  / OC1A / PCINT9          (ATtinyCore D9)
D10 = "PB2"   # SCK  / USCK / SCL / INT0 / PCINT10  (ATtinyCore D10)
# PB3 = RESET / PCINT11 -- GPIO requires RSTDISBL fuse (not exposed here)

# Analog channels (Port A)
A0 = "PA0"   # ADC0
A1 = "PA1"   # ADC1
A2 = "PA2"   # ADC2
A3 = "PA3"   # ADC3
A4 = "PA4"   # ADC4
A5 = "PA5"   # ADC5
A6 = "PA6"   # ADC6
A7 = "PA7"   # ADC7

# Named aliases
SCK  = "PB2"   # D10 / USI USCK
MOSI = "PB0"   # D8  / USI MOSI / DI
MISO = "PB1"   # D9  / USI MISO / DO
SCL  = "PB2"   # D10 / USI SCL
SDA  = "PB0"   # D8  / USI SDA
INT0 = "PB2"   # D10 / External interrupt 0

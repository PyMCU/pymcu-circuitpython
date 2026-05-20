# CircuitPython-style board pin constants for Digispark (ATtiny85 @ 16.5 MHz USB)
#
# Digispark uses P0-P5 naming matching the silk-screen.
# Note: P5 = PB5 = RESET -- usable as GPIO only with RSTDISBL fuse set.
#
# No hardware UART. SPI/I2C use USI (bit-bang) on P0/P2.

# Digital pins (Digispark silk-screen numbering)
P0 = "PB0"   # MOSI / SDA / OC1A / PCINT0
P1 = "PB1"   # MISO / OC0B / OC1A / PCINT1 / LED
P2 = "PB2"   # SCK  / SCL  / ADC1 / INT0   / PCINT2
P3 = "PB3"   # ADC3 / PCINT3
P4 = "PB4"   # ADC2 / PCINT4
P5 = "PB5"   # ADC0 / RESET / dW  / PCINT5 -- requires RSTDISBL fuse!

# Analog channels (ADC mux codes; actual pin is port string above)
A0 = "PB5"   # ADC0 -- requires RSTDISBL fuse
A1 = "PB2"   # ADC1
A2 = "PB4"   # ADC2
A3 = "PB3"   # ADC3

# Named aliases
LED         = "PB1"   # P1 built-in LED
LED_BUILTIN = "PB1"
SCK  = "PB2"   # P2 / USI SCK
MOSI = "PB0"   # P0 / USI MOSI/DI
MISO = "PB1"   # P1 / USI MISO/DO  (shared with LED)
SCL  = "PB2"   # P2 / USI SCL
SDA  = "PB0"   # P0 / USI SDA

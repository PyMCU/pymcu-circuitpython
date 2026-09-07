# CircuitPython-style board pin constants for Adafruit Trinket 5V (ATtiny85 @ 16 MHz)
#
# Adafruit silk-screens the five usable pins as #0-#4, and Adafruit's own
# CircuitPython boards spell them D0-D4, so both names are provided.
#
# The red on-board LED is on #1 (PB1), shared with MISO. PB5 is RESET and is not
# exposed here: driving it needs the RSTDISBL fuse, after which the board can no
# longer be programmed over ISP, so it is not something a `board.` constant
# should hand out by accident.
#
# No hardware UART. SPI/I2C are USI (bit-bang) on #0/#2.

# Digital pins (Adafruit silk-screen #0-#4)
D0 = "PB0"   # MOSI / SDA / OC1A / PCINT0
D1 = "PB1"   # MISO / OC0B / OC1A / PCINT1 -- red on-board LED
D2 = "PB2"   # SCK  / SCL  / ADC1 / INT0   / PCINT2
D3 = "PB3"   # ADC3 / PCINT3 -- shared with USB D-
D4 = "PB4"   # ADC2 / PCINT4 -- shared with USB D+

# Analog channels, using Adafruit's numbering: #2 is A1, #4 is A2, #3 is A3.
# There is no A0: that channel is ADC0 on PB5, which is RESET on this board.
A1 = "PB2"   # ADC1 on #2
A2 = "PB4"   # ADC2 on #4
A3 = "PB3"   # ADC3 on #3

# Named aliases
LED         = "PB1"   # #1 red on-board LED
LED_BUILTIN = "PB1"
SCK  = "PB2"   # #2 / USI SCK
MOSI = "PB0"   # #0 / USI MOSI/DI
MISO = "PB1"   # #1 / USI MISO/DO  (shared with the LED)
SCL  = "PB2"   # #2 / USI SCL
SDA  = "PB0"   # #0 / USI SDA

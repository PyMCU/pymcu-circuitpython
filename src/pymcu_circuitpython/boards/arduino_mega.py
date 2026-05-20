# CircuitPython-style board pin constants for Arduino Mega 2560 (ATmega2560 @ 16 MHz)
#
# Pin mapping follows the official Arduino Mega 2560 silk-screen numbering.
# Digital D0-D53, Analog A0-A15, plus CircuitPython canonical aliases.
#
# Note: explicit string literals are required here because the PyMCU compiler only
# registers module-level globals for explicit assignments, not re-exported imports.

# Digital pins D0-D13 (Port E, G, H, B)
D0  = "PE0"   # RX0 / PCINT8
D1  = "PE1"   # TX0 / PCINT9
D2  = "PE4"   # INT4 / OC3B / PCINT4
D3  = "PE5"   # INT5 / OC3C / PCINT5
D4  = "PG5"   # OC0B
D5  = "PE3"   # AIN1 / OC3A / PCINT3
D6  = "PH3"   # OC4A / PCINT3
D7  = "PH4"   # OC4B / PCINT4
D8  = "PH5"   # OC4C / PCINT5
D9  = "PH6"   # OC2B / PCINT6
D10 = "PB4"   # OC2A / PCINT4
D11 = "PB5"   # OC1A / PCINT5
D12 = "PB6"   # OC1B / PCINT6
D13 = "PB7"   # OC0A / OC1C / PCINT7 / LED

# Digital pins D14-D21 (serial + I2C)
D14 = "PJ1"   # TX3 / PCINT10
D15 = "PJ0"   # RX3 / PCINT9
D16 = "PH1"   # TX2 / PCINT1
D17 = "PH0"   # RX2 / PCINT0
D18 = "PD3"   # TX1 / INT3
D19 = "PD2"   # RX1 / INT2
D20 = "PD1"   # SDA / INT1
D21 = "PD0"   # SCL / INT0

# Digital pins D22-D29 (Port A)
D22 = "PA0"
D23 = "PA1"
D24 = "PA2"
D25 = "PA3"
D26 = "PA4"
D27 = "PA5"
D28 = "PA6"
D29 = "PA7"

# Digital pins D30-D37 (Port C, reversed)
D30 = "PC7"
D31 = "PC6"
D32 = "PC5"
D33 = "PC4"
D34 = "PC3"
D35 = "PC2"
D36 = "PC1"
D37 = "PC0"

# Digital pins D38-D41 (Port D/G)
D38 = "PD7"
D39 = "PG2"
D40 = "PG1"
D41 = "PG0"

# Digital pins D42-D49 (Port L, reversed)
D42 = "PL7"
D43 = "PL6"
D44 = "PL5"   # OC5C
D45 = "PL4"   # OC5B
D46 = "PL3"   # OC5A
D47 = "PL2"
D48 = "PL1"
D49 = "PL0"

# Digital pins D50-D53 (Port B, SPI)
D50 = "PB3"   # MISO / PCINT3
D51 = "PB2"   # MOSI / PCINT2
D52 = "PB1"   # SCK  / PCINT1
D53 = "PB0"   # SS   / PCINT0

# Analog pins A0-A7 (Port F, ADC0-ADC7)
A0  = "PF0"   # ADC0
A1  = "PF1"   # ADC1
A2  = "PF2"   # ADC2
A3  = "PF3"   # ADC3
A4  = "PF4"   # ADC4
A5  = "PF5"   # ADC5
A6  = "PF6"   # ADC6
A7  = "PF7"   # ADC7

# Analog pins A8-A15 (Port K, ADC8-ADC15 via MUX5)
A8  = "PK0"   # ADC8
A9  = "PK1"   # ADC9
A10 = "PK2"   # ADC10
A11 = "PK3"   # ADC11
A12 = "PK4"   # ADC12
A13 = "PK5"   # ADC13
A14 = "PK6"   # ADC14
A15 = "PK7"   # ADC15

# CircuitPython canonical aliases
LED         = "PB7"   # D13 built-in LED
LED_BUILTIN = "PB7"
TX   = "PE1"   # D1  / USART0 TX
RX   = "PE0"   # D0  / USART0 RX
TX1  = "PD3"   # D18 / USART1 TX
RX1  = "PD2"   # D19 / USART1 RX
TX2  = "PH1"   # D16 / USART2 TX
RX2  = "PH0"   # D17 / USART2 RX
TX3  = "PJ1"   # D14 / USART3 TX
RX3  = "PJ0"   # D15 / USART3 RX
SCL  = "PD0"   # D21 / TWI SCL
SDA  = "PD1"   # D20 / TWI SDA
SCK  = "PB1"   # D52 / SPI SCK
MOSI = "PB2"   # D51 / SPI MOSI
MISO = "PB3"   # D50 / SPI MISO
SS   = "PB0"   # D53 / SPI SS

# CircuitPython-style board pin constants for Arduino Micro (ATmega32U4 @ 16 MHz)
#
# Pin mapping follows the official Arduino Micro silk-screen numbering.
# Digital D0-D13, Analog A0-A5, plus CircuitPython canonical aliases.
#
# Note: explicit string literals are required here because the PyMCU compiler only
# registers module-level globals for explicit assignments, not re-exported imports.

# Digital pins
D0  = "PD2"   # RX  / INT2
D1  = "PD3"   # TX  / INT3
D2  = "PD1"   # SDA / INT1
D3  = "PD0"   # SCL / INT0 / OC0B
D4  = "PD4"   # ADC8 / ICP1
D5  = "PC6"   # OC3A / #OC4A
D6  = "PD7"   # OC4D / ADC10 / T0
D7  = "PE6"   # INT6 / AIN0
D8  = "PB4"   # PCINT4 / ADC11
D9  = "PB5"   # PCINT5 / OC1A / #OC4B / ADC12
D10 = "PB6"   # PCINT6 / OC1B / OC4B / ADC13
D11 = "PB7"   # PCINT7 / OC0A / OC1C / #RTS
D12 = "PD6"   # T1 / #OC4D / ADC9
D13 = "PC7"   # ICP3 / CLK0 / OC4A / LED

# Analog pins (Port F, ADC channels in reverse order on Micro)
A0 = "PF7"   # ADC7
A1 = "PF6"   # ADC6
A2 = "PF5"   # ADC5
A3 = "PF4"   # ADC4
A4 = "PF1"   # ADC1
A5 = "PF0"   # ADC0

# CircuitPython canonical aliases
LED         = "PC7"   # D13 built-in LED
LED_BUILTIN = "PC7"
TX   = "PD3"   # D1  / USART1 TX
RX   = "PD2"   # D0  / USART1 RX
SCL  = "PD0"   # D3  / TWI SCL
SDA  = "PD1"   # D2  / TWI SDA
SCK  = "PB1"   # ICSP SCK  / PCINT1
MOSI = "PB2"   # ICSP MOSI / PCINT2
MISO = "PB3"   # ICSP MISO / PCINT3
SS   = "PB0"   # ICSP SS   / PCINT0

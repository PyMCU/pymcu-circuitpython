# CircuitPython-style board pin constants for ATtiny2313 bare chip (20-pin DIP)
# Also pin-compatible with ATtiny4313 (4KB flash, 256B SRAM).
#
# Port D: PD0-PD6 (7 pins; PD0=RX, PD1=TX)
# Port B: PB0-PB7 (8 pins)
# Port A: PA0 (XTAL1), PA1 (XTAL2) -- typically used for clock, not GPIO
# No ADC. Hardware UART on PD0/PD1. USI (bit-bang SPI/I2C) on PB5-PB7.

# Port D
D0 = "PD0"   # RXD  / PCINT11
D1 = "PD1"   # TXD  / PCINT12
D2 = "PD2"   # INT0 / PCINT13
D3 = "PD3"   # INT1 / PCINT14
D4 = "PD4"   # XCK  / T0 / PCINT15
D5 = "PD5"   # OC0B / T1 / PCINT16
D6 = "PD6"   # ICP  / OC1A / PCINT17

# Port B
D7  = "PB0"   # MOSI / DI  / SDA / OC0A / PCINT0
D8  = "PB1"   # MISO / DO  / PCINT1
D9  = "PB2"   # SCK  / USCK / SCL / PCINT2
D10 = "PB3"   # OC1B / PCINT3
D11 = "PB4"   # OC1A / PCINT4
D12 = "PB5"   # PCINT5
D13 = "PB6"   # PCINT6
D14 = "PB7"   # PCINT7

# Named aliases
TX   = "PD1"
RX   = "PD0"
SCK  = "PB2"   # USI USCK
MOSI = "PB0"   # USI DI
MISO = "PB1"   # USI DO
SCL  = "PB2"   # USI SCL
SDA  = "PB0"   # USI SDA
INT0 = "PD2"
INT1 = "PD3"

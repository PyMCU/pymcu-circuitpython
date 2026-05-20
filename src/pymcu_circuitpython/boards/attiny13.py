# CircuitPython-style board pin constants for ATtiny13 bare chip (8-pin DIP)
# Also pin-compatible with ATtiny13A (same package, improved oscillator).
#
# PORTB only: PB0-PB4 usable as GPIO. PB5 = RESET (GPIO requires RSTDISBL fuse).
# Very minimal: 1KB flash, 64B SRAM, 64B EEPROM. No UART, no USI.
# ADC on PB2-PB5 (4 channels: ADC1/ADC0 most useful).

PB0 = "PB0"   # MOSI / OC0A / AIN0 / PCINT0
PB1 = "PB1"   # MISO / OC0B / INT0 / AIN1 / PCINT1
PB2 = "PB2"   # SCK  / ADC1 / T0   / PCINT2
PB3 = "PB3"   # ADC3 / CLKI / PCINT3
PB4 = "PB4"   # ADC2 / PCINT4
PB5 = "PB5"   # ADC0 / RESET / dW / PCINT5 -- GPIO requires RSTDISBL fuse!

A0 = "PB5"   # ADC0 -- requires RSTDISBL fuse
A1 = "PB2"   # ADC1
A2 = "PB4"   # ADC2
A3 = "PB3"   # ADC3

INT0 = "PB1"

# CircuitPython-style board pin constants for ATtiny13A bare chip (8-pin DIP)
# Same pinout as ATtiny13 (improved internal oscillator). See attiny13.py for details.

PB0 = "PB0"; PB1 = "PB1"; PB2 = "PB2"
PB3 = "PB3"; PB4 = "PB4"
PB5 = "PB5"   # RESET by default -- GPIO requires RSTDISBL fuse!

A0 = "PB5"; A1 = "PB2"; A2 = "PB4"; A3 = "PB3"

INT0 = "PB1"

# Dn numbering (#4). ATtinyCore and the Digispark silkscreen both number PB0..PB5
# as 0..5, so this is the spelling published snippets for these parts use. There
# is deliberately no LED: a bare DIP has none, and the only free leg left to point
# it at would be PB5, which is RESET.
D0 = "PB0"
D1 = "PB1"
D2 = "PB2"
D3 = "PB3"
D4 = "PB4"
D5 = "PB5"   # RESET by default -- GPIO requires RSTDISBL fuse!

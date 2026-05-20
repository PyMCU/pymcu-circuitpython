# Board -> chip mapping for boards known to the CircuitPython flavor.
# The PyMCU build driver merges this into its own BOARD_CHIPS dict at build time.
# Extension entries take precedence over the built-in driver mapping.
#
# IMPORTANT: Only add boards for chips with FULLY WORKING codegen support.
# As of now, PyMCU only has complete AVR codegen. Do not add boards for
# unsupported architectures (SAMD21, RP2040, PIC18, etc.) until their
# backends are fully implemented and tested.
#
# The driver already includes Arduino board mappings (Uno, Nano, Mega, Micro).
# This file is for additional CircuitPython-specific boards that use AVR chips.

BOARD_CHIPS: dict = {
    # ATtiny named dev boards (supplement to driver's built-in BOARD_CHIPS)
    "digispark":        "attiny85",
    "adafruit_trinket": "attiny85",
    # ATtiny bare chips -- 8-pin
    "attiny85":  "attiny85",
    "attiny45":  "attiny45",
    "attiny25":  "attiny25",
    "attiny13":  "attiny13",
    "attiny13a": "attiny13a",
    # ATtiny bare chips -- 14-pin
    "attiny84": "attiny84",
    "attiny44": "attiny44",
    "attiny24": "attiny24",
    # ATtiny bare chips -- 20-pin
    "attiny2313": "attiny2313",
    "attiny4313": "attiny4313",
}

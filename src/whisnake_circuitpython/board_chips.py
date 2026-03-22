# Board -> chip mapping for boards known to the CircuitPython flavor.
# The Whisnake build driver merges this into its own BOARD_CHIPS dict at build time.
# Extension entries take precedence over the built-in driver mapping.
#
# IMPORTANT: Only add boards for chips with FULLY WORKING codegen support.
# As of now, Whisnake only has complete AVR codegen. Do not add boards for
# unsupported architectures (SAMD21, RP2040, PIC18, etc.) until their
# backends are fully implemented and tested.
#
# The driver already includes Arduino board mappings (Uno, Nano, Mega, Micro).
# This file is for additional CircuitPython-specific boards that use AVR chips.

BOARD_CHIPS: dict = {
    # Currently empty - all AVR Arduino boards are already in the driver
    # Add AVR-based CircuitPython boards here when needed, e.g.:
    # "adafruit_metro_m0_express": "atmega328p",  # if it existed
}

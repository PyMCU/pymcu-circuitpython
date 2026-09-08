# CircuitPython-compatible micropython module for PyMCU
#
# CircuitPython ships a `micropython` module, and the only name it documents is
# const().  Adafruit libraries open with `from micropython import const` so the
# same source runs under CircuitPython and MicroPython alike, so a
# CircuitPython project has to be able to resolve that import.
#
# Only const() is provided here, deliberately.  MicroPython's module carries
# more (native, viper, mem_info, heap_lock and the rest); CircuitPython does
# not document those, and a name that exists here but not on a real board is
# the failure this layer exists to prevent.  The MicroPython flavor
# (pymcu_micropython.micropython) offers the wider surface where it belongs.
#
# Usage:
#   from micropython import const
#   _REG_CONFIG = const(0x00)

from pymcu.types import inline


@inline
def const(value):
    """Declare that an expression is a compile-time constant.

    Identity in PyMCU: integer literals and const[T]-annotated names are
    already folded at compile time, so const(x) hands the compiler the literal
    directly, which is the effect CircuitPython documents.
    """
    return value

# CircuitPython-compatible array module for PyMCU
#
# `import array` in a CircuitPython driver (adafruit_dht buffers its pulse train
# in `array.array("H")`) resolves here; `array.array(typecode)` itself is
# recognized by the compiler from the call shape, the same place bytearray()
# and list() already are -- this class exists so the import resolves and
# `array.array` names something. There is no body: the compiler lowers the call
# to the heap-bounded list[T] it already has.
class array:
    pass

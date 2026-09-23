# circuitpython_typing for PyMCU
#
# Upstream (adafruit/Adafruit_CircuitPython_Typing) is a pure-annotation
# package: every name in it exists for static checkers and is imported under
# `try: ... except ImportError:` guards, so a board without it still runs.
#
# Most of that surface stays unbound here on purpose -- names like
# ReadableBuffer / WriteableBuffer are annotation-only and PyMCU reads
# annotations straight from the source, so the guarded import failing is the
# correct outcome for them. What cannot stay unbound is a Protocol class used
# inside a Union[...] parameter (e.g. adafruit_debouncer's
# `Union[ROValueIO, Callable[[], bool]]`): the compiler's structural Protocol
# match needs a real scanned class to check members against, which is why
# `io.py` here defines ROValueIO / ValueIO for real.
#
# ReadableBuffer / WriteableBuffer DO need a binding at the package root:
# `from circuitpython_typing import ReadableBuffer` fails hard when the
# package exists but lacks the name (a missing MODULE trips the guard, a
# missing name does not). Empty classes keep them annotation-only -- nothing
# in the supported libraries puts them inside a Union[...], which is the only
# annotation form whose arguments get structurally matched.

class ReadableBuffer:
    pass

class WriteableBuffer:
    pass

class ByteStream:
    pass

class I2CDeviceDriver:
    pass

class SPIDeviceDriver:
    pass

# CircuitPython-compatible os module for PyMCU
#
# `from os import uname` in a CircuitPython driver resolves here. pymcu.os owns
# the facts -- uname() reports sysname "PyMCU" and the chip name as machine, so
# `"Linux" not in uname()` (adafruit_dht's CircuitPython-vs-Blinka test) folds
# to the CircuitPython arm.
from pymcu.os import uname, uname_result

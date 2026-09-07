# CircuitPython-compat wifi.radio over the CYW43439 (Pico 2 W). The module-level radio
# IS the CYW43 driver (its connect()/publish() convenience methods).
from pymcu.hal.wifi import CYW43

radio = CYW43()

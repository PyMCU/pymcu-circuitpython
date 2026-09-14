"""
Inject pymcu.hal.* stubs into sys.modules so that pymcu_circuitpython modules
can be imported in standard CPython without MCU hardware.

This file is loaded by pytest before any test module, so the mocks are in place
when the package-under-test runs its top-level imports.
"""
import sys
from types import ModuleType
from unittest.mock import MagicMock


def _install_hal_mocks() -> None:
    # Guard: only install once per process.
    if "pymcu.hal" in sys.modules:
        return

    # --- concrete mock classes ------------------------------------------ #

    class _MockPin:
        IN = 1
        OUT = 0
        OPEN_DRAIN = 2
        PULL_UP = 1

        def __init__(self, name, mode=1):
            self._name = name
            self._mode = mode
            self._v = 0

        def high(self):   self._v = 1
        def low(self):    self._v = 0
        def on(self):     self._v = 1
        def off(self):    self._v = 0
        def toggle(self): self._v ^= 1

        def value(self, x=None):
            if x is None:
                return self._v
            self._v = x
            return x

        def mode(self, m=None):
            if m is None:
                return self._mode
            self._mode = m

        def pull(self, p):    pass
        def irq(self, trigger=None, handler=None): pass

    class _MockUART:
        def __init__(self, baudrate=9600): pass
        def write(self, data):   pass
        def read(self):          return 0
        def read_nb(self):       return 0
        def available(self):     return 0

    class _MockAnalogPin:
        def __init__(self, pin): pass
        def start(self):         pass
        def read(self):          return 0

    class _MockPWM:
        def __init__(self, pin, duty=0, freq=500): pass
        def start(self):          pass
        def stop(self):           pass
        def deinit(self):         pass
        def set_duty(self, d):    pass
        def set_freq(self, freq):  self._freq = freq

    class _MockSPI:
        def __init__(self, mode=0, cs=""): pass
        def transfer(self, data): return 0
        def write(self, data):    pass
        def select(self):         pass
        def deselect(self):       pass

    class _MockEEPROM:
        # Class-level store so reads see prior writes even though the nvm
        # accessors construct a fresh EEPROM() on every call (zero-cost inline).
        _store: dict = {}
        def __init__(self):              pass
        def write(self, addr, value):    _MockEEPROM._store[addr] = value & 0xFF
        def read(self, addr):            return _MockEEPROM._store.get(addr, 0)

    class _MockI2C:
        def __init__(self):          pass
        def ping(self, addr):        return 0
        def write_to(self, addr, d): return 0
        def read_from(self, addr):   return 0
        def read_ack(self):          return 0
        def read_nack(self):         return 0
        def start(self):             pass
        def stop(self):              pass
        def write(self, data):       pass
        def read(self):              return 0

    # --- register hal sub-modules --------------------------------------- #

    hal = ModuleType("pymcu.hal")
    sys.modules["pymcu.hal"] = hal

    # pymcu.hal.irq: microcontroller.enable_interrupts / disable_interrupts wrap these.
    irq = ModuleType("pymcu.hal.irq")
    irq.enable_interrupts = lambda: None
    irq.disable_interrupts = lambda: None
    sys.modules["pymcu.hal.irq"] = irq
    hal.irq = irq

    def _reg(name: str, **attrs) -> ModuleType:
        m = ModuleType(f"pymcu.hal.{name}")
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[f"pymcu.hal.{name}"] = m
        setattr(hal, name, m)
        return m

    _reg("gpio",     Pin=_MockPin)
    _reg("uart",     UART=_MockUART)
    _reg("adc",      AnalogPin=_MockAnalogPin)
    _reg("pwm",      PWM=_MockPWM)
    _reg("spi",      SPI=_MockSPI)
    _reg("i2c",      I2C=_MockI2C)
    _reg("watchdog", Watchdog=MagicMock)
    _reg("eeprom",   EEPROM=_MockEEPROM)
    _reg("timer",    millis=lambda: 0, millis_init=lambda: None)

    # --- pymcu.time (time.py / utime.py import delay_ms, delay_us) ------ #
    # The real pymcu.time imports __CHIP__ from pymcu.chips at module load,
    # which is a compile-time constant injected by the compiler.  It is not
    # present at runtime in CPython, so we replace the whole module.
    time_mod = ModuleType("pymcu.time")
    time_mod.delay_ms = lambda ms: None
    time_mod.delay_us = lambda us: None
    sys.modules["pymcu.time"] = time_mod

    # --- pymcu.chips (microcontroller.py uses device_info) -------------- #
    class _DeviceInfo:
        frequency = 16_000_000

    # __CHIP__ is the object the compiler binds to the target: the modules read
    # __CHIP__.arch and __CHIP__.name (they used to compare it with a string, and
    # a string here left five of the nine test modules failing at import).
    class _Chip:
        arch = "avr"
        name = "atmega328p"
        family = "avr"
        ram_size = 2048
        flash_size = 32768
        frequency = 16_000_000

        def __str__(self):
            return self.name

    chips = ModuleType("pymcu.chips")
    chips.__CHIP__ = _Chip()
    chips.__FREQ__ = 16_000_000
    chips.__TIMEBASE__ = 0
    # The compiler binds __FREQ__ as a name every module can read without importing it
    # (microcontroller.cpu.frequency returns it bare); under CPython it is a builtin here.
    import builtins
    builtins.__FREQ__ = 16_000_000
    builtins.__TIMEBASE__ = 0
    chips.device_info = lambda: _DeviceInfo()
    sys.modules["pymcu.chips"] = chips



_install_hal_mocks()


# A CircuitPython program spells its own modules by their top-level names, and so does the
# layer when one module needs another (`from watchdog import WatchDogMode` inside
# microcontroller.py). The compiler resolves those names to the layer; under CPython this
# finder does the same, for any top-level name that is a module of the package.
import importlib.abc
import importlib.machinery
import importlib.util
import pkgutil
import pymcu_circuitpython as _layer

_LAYER_MODULES = {m.name for m in pkgutil.iter_modules(_layer.__path__)}


class _LayerAlias(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if path is not None or fullname not in _LAYER_MODULES or fullname in sys.modules:
            return None
        real = importlib.import_module(f"pymcu_circuitpython.{fullname}")
        sys.modules[fullname] = real
        return importlib.util.spec_from_loader(fullname, loader=None)


sys.meta_path.insert(0, _LayerAlias())

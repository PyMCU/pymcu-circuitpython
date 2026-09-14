"""
Inject pymcu.hal.* stubs into sys.modules so that pymcu_circuitpython modules
can be imported in standard CPython without MCU hardware.

This file is loaded by pytest before any test module, so the mocks are in place
when the package-under-test runs its top-level imports.
"""
import sys
from types import ModuleType
from unittest.mock import MagicMock

from pymcu.exceptions import CompileError


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

        def pull(self, p):    self._pull = p
        def irq(self, trigger=None, handler=None): pass

    class _MockUART:
        # In step with pymcu.hal.uart.UART: the frame format reaches the constructor, the
        # receive ring has a count and a capacity, and a read can time out.
        def __init__(self, baudrate=9600, bits=8, parity=0, stop=1):
            self.bits, self.parity, self.stop = bits, parity, stop
            self._ring = []
            self._buffered = False

        def write(self, data):   pass
        def read(self):          return 0
        def read_nb(self):       return self._ring.pop(0) if self._ring else 0
        def available(self):     return 1 if self._ring else 0

        def rx_count(self):       return len(self._ring)
        def rx_buffer_size(self): return 64
        def rx_read(self):        return self._ring.pop(0) if self._ring else 0

        def start_buffered_rx(self, size=0):
            if size > 64:
                raise CompileError(
                    "this UART's receive ring holds 64 bytes and cannot be sized per "
                    "program: it is a fixed array in the HAL, allocated at compile time.")
            self._buffered = True

        def rx_read_timeout(self, ms):
            return self._ring.pop(0) if self._ring else -1

        def read_timeout(self, ms):
            return self._ring.pop(0) if self._ring else -1

    class _MockAnalogPin:
        # In step with pymcu.hal.adc.AnalogPin: read() is the raw converter count,
        # read_u16() the same reading scaled to the full 16-bit range (bit replication,
        # not a shift), and the reference accessors are the chip's, not the layer's.
        WIDTH = 10

        def __init__(self, pin): pass
        def start(self):         pass
        def read(self):          return 0

        def read_u16(self):
            raw = self.read()
            return (raw << 6) | (raw >> 4)

        def reference_millivolts(self): return 5000
        def reference_volts(self):      return 5.0

    class _MockPWM:
        # In step with pymcu.hal.pwm.PWM: frequency() reports what the pin emits, which is
        # not the request. A Timer1 channel (PB1/PB2) asking for something that is not one of
        # the eight-bit buckets reaches the mode whose period is a register and comes out
        # exactly; every other pin lands on the nearest bucket.
        BUCKETS = (62500, 7812, 976, 244, 61)

        def __init__(self, pin, duty=0, freq=500, invert=0, duty_u16=0):
            self._pin, self._freq = pin, freq
            self.duty_u16 = duty_u16

        def start(self):          pass
        def stop(self):           pass
        def deinit(self):         pass
        def set_duty(self, d):    pass

        def set_duty_u16(self, d): self.duty_u16 = d

        def set_freq(self, freq):  self._freq = freq

        def frequency(self):
            if self._freq == 0:
                return 976
            if self._pin in ("PB1", "PB2") and self._freq not in self.BUCKETS:
                return self._freq
            return min(self.BUCKETS, key=lambda b: abs(b - self._freq))

    class _MockSPI:
        # In step with pymcu.hal.spi.SPI: the clock rate and the mode reach the constructor
        # and configure(), and frequency() reports what the dividers can actually produce.
        def __init__(self, mode=0, cs="", baudrate=4000000, polarity=0, phase=0,
                     lsb_first=0):
            self.configure(baudrate, polarity, phase, lsb_first)

        def configure(self, baudrate=4000000, polarity=0, phase=0, lsb_first=0):
            self.baudrate, self.polarity, self.phase = baudrate, polarity, phase

        def frequency(self):
            for div in (2, 4, 8, 16, 32, 64, 128):
                if 16_000_000 // div <= self.baudrate:
                    return 16_000_000 // div
            return 16_000_000 // 128

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

        # In step with pymcu.hal.eeprom.EEPROM: the size is the part's, not a constant the
        # layer keeps. The mock chip is an ATmega328P.
        def size(self):                  return 1024

    class _MockDACPin:
        # In step with pymcu.hal.dac.DACPin: no AVR part has a converter, so constructing
        # one is refused where it is written instead of compiling to nothing.
        def __init__(self, pin=""):
            raise CompileError(
                "this chip has no digital-to-analog converter. No AVR part has one, so "
                "there is nothing to drive a steady analog voltage with. Use pymcu.hal.pwm "
                "(PWM(pin, duty_u16=...)) and an RC low-pass filter on the pin for an "
                "analog-like output, or drive an external converter over SPI or I2C.")

        def set_value_u16(self, value): pass
        def deinit(self):               pass

    class _MockPulseCapture:
        # In step with pymcu.hal.pulse.PulseCapture: a queue of microsecond durations, a
        # capacity the HAL fixes at compile time, and a maxlen larger than it refused.
        CAPACITY = 128

        def __init__(self, pin, maxlen=2, idle_state=0):
            if maxlen > self.CAPACITY:
                raise CompileError(
                    "this pulse capture can hold 128 pulses and cannot be sized per program: "
                    "the buffer is a fixed array in the HAL, allocated at compile time.")
            if maxlen == 0:
                raise CompileError(
                    "a pulse capture with room for no pulses would record nothing.")
            self._maxlen = maxlen
            self._q: list = []
            self._paused = 0

        def feed(self, *durations):
            """Test-only: what the pin would have produced."""
            for d in durations:
                if not self._paused and len(self._q) < self._maxlen:
                    self._q.append(d)

        def count(self):     return len(self._q)
        def maxlen(self):    return self._maxlen
        def capacity(self):  return self.CAPACITY
        def get(self, i):    return self._q[i] if i < len(self._q) else 0
        def popleft(self):   return self._q.pop(0) if self._q else 0
        def clear(self):     self._q.clear()
        def pause(self):     self._paused = 1
        def resume(self):    self._paused = 0
        def paused(self):    return self._paused
        def deinit(self):    self._paused = 1

    class _MockPulseTrain:
        # In step with pymcu.hal.pulse.PulseTrain: the carrier comes out of one pin, and any
        # other is refused where the train is written.
        PIN = "PD3"

        def __init__(self, pin, freq=38000, duty_u16=32768):
            if pin != self.PIN:
                raise CompileError(
                    "a pulse train's carrier comes out of OC2B, which is PD3 (D3 on an "
                    "Arduino board) and nothing else on this part.")
            if freq < 7800 or freq > 1000000:
                raise CompileError(
                    "this carrier frequency is outside what Timer2 reaches as this HAL "
                    "programs it: about 7.8 kHz to 1 MHz at a 16 MHz clock.")
            self.freq, self.duty = freq, duty_u16
            self.sent: list = []

        def send(self, pulses, n):
            self.sent = list(pulses[:n])

        def carrier_on(self):  pass
        def carrier_off(self): pass
        def deinit(self):      pass

    class _MockSoftI2C:
        # In step with pymcu.hal.softi2c.SoftI2C: an open-drain bus that logs what it
        # clocked out, so a test can read the transfer the way a logic analyser would.
        def __init__(self, scl, sda, half_us=5):
            self.scl, self.sda, self.half_us = scl, sda, half_us
            self.log: list = []

        def init(self):              self.log.append("idle")
        def start(self):             self.log.append("S")
        def stop(self):              self.log.append("P")
        def write(self, data):       self.log.append(data); return 0
        def read(self, send_ack):    self.log.append("R" + ("A" if send_ack else "N")); return 0
        def ping(self, addr):        return 1

    class _MockSoftSPI:
        # In step with pymcu.hal.softspi.SoftSPI: mode 0 only, and a half-period in whole
        # microseconds that set_baudrate recomputes.
        def __init__(self, sck, mosi, miso, mode=0, cs=None, baudrate=500):
            self.sck, self.mosi, self.miso = sck, mosi, miso
            self.set_baudrate(baudrate)
            self.mosi_log: list = []

        def set_baudrate(self, baudrate):
            self.half_us = 500 // baudrate

        def transfer(self, data):
            self.mosi_log.append(data)
            return 0

    class _MockEdgeCounter:
        # In step with pymcu.hal.counter.EdgeCounter. Rising and falling are told apart only
        # on the two pins with a dedicated interrupt; every other pin has a pin-change
        # interrupt that fires on both and cannot say which, so asking it for one is refused.
        SINGLE_EDGE_PINS = ("PD2", "PD3", 2, 3)

        def __init__(self, pin, edge=2, pull=1):
            if edge > 2:
                raise CompileError("an edge is 0 (both), 1 (rising) or 2 (falling).")
            if edge != 0 and pin not in self.SINGLE_EDGE_PINS:
                raise CompileError(
                    "this pin can only count BOTH edges. Rising and falling are told apart "
                    "by INT0 and INT1, which are PD2 and PD3.")
            self.pin, self.edge, self.pull = pin, edge, pull
            self._count = 0

        def tick(self, n=1):
            """Test-only: what the pin would have done."""
            self._count += n

        def count(self):  return self._count
        def reset(self):  self._count = 0

    class _MockQuadrature:
        # In step with pymcu.hal.encoder.Quadrature, including the decoder: the state is
        # (A << 1) | B, nothing changing and both changing at once are not a direction, and
        # the old state's high bit exclusive-ored with the new state's low bit says which way.
        # Both lines have to be on one port, because the handler reads one port register.
        PORT_OF = {"B": "B", "C": "C", "D": "D"}

        def __init__(self, pin_a, pin_b, pull=1):
            if self._port(pin_a) != self._port(pin_b):
                raise CompileError(
                    "an encoder's two lines have to be on the same port.")
            if pin_a == pin_b:
                raise CompileError(
                    "an encoder's two lines have to be two different pins.")
            self.pin_a, self.pin_b, self.pull = pin_a, pin_b, pull
            # An encoder idles with both lines released, which with the pull-ups on reads 11
            # and not 00. The decoder is primed from the lines, not started at zero.
            self._state = 3 if pull else 0
            self._pos = 0

        @staticmethod
        def _port(pin):
            if isinstance(pin, str):
                return pin[1]
            if pin <= 7:
                return "D"
            if pin <= 13:
                return "B"
            return "C"

        def lines(self, a, b):
            """Test-only: what the two lines would be showing now."""
            now = (1 if a else 0) * 2 + (1 if b else 0)
            moved = self._state ^ now
            if moved != 0 and moved != 3:
                if ((self._state >> 1) ^ now) & 1:
                    self._pos += 1
                else:
                    self._pos -= 1
            self._state = now

        def position(self):
            return self._pos

        def set_position(self, value):
            self._pos = value

    class _MockI2C:
        # In step with pymcu.hal.i2c.I2C: the SCL rate reaches the constructor, and
        # frequency() reports what the integer bit-rate register can actually clock.
        def __init__(self, addr=0, general_call=0, freq=100000):
            self._freq = freq

        def frequency(self):
            twbr = (16_000_000 // self._freq - 16) // 2
            return 16_000_000 // (16 + 2 * twbr)

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
    _reg("dac",      DACPin=_MockDACPin)
    _reg("pulse",    PulseCapture=_MockPulseCapture, PulseTrain=_MockPulseTrain)
    _reg("softi2c",  SoftI2C=_MockSoftI2C)
    _reg("softspi",  SoftSPI=_MockSoftSPI)
    _reg("counter",  EdgeCounter=_MockEdgeCounter)
    _reg("encoder",  Quadrature=_MockQuadrature)
    _reg("pwm",      PWM=_MockPWM)
    _reg("spi",      SPI=_MockSPI)
    _reg("i2c",      I2C=_MockI2C)
    _reg("watchdog", Watchdog=MagicMock)
    _reg("eeprom",   EEPROM=_MockEEPROM)
    # millis() ADVANCES. A clock that always reads zero is not a clock: alarm's polling
    # loop waits on it, so a constant made the loop run for ever. One millisecond a call is
    # the cheapest thing that behaves like time passing.
    class _Clock:
        now = 0

        @classmethod
        def millis(cls):
            cls.now += 1
            return cls.now

    _reg("timer",    millis=_Clock.millis, millis_init=lambda: None)

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

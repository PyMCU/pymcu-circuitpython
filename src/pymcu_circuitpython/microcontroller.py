# CircuitPython-compatible microcontroller module for PyMCU
#
# Mirrors CircuitPython's microcontroller module: microcontroller.cpu (a
# Processor instance), microcontroller.reset() and microcontroller.delay_us().
#
# Usage:
#   import microcontroller
#   hz   = microcontroller.cpu.frequency     # CPU frequency in Hz (compile-time)
#   degc = microcontroller.cpu.temperature   # die temperature in C (soft-float)
#   v    = microcontroller.cpu.voltage       # Vcc in volts (soft-float)
#   microcontroller.reset()                  # reset the MCU (watchdog)

from pymcu.types import uint8, uint16, uint32, inline, const, warning
from pymcu.chips import device_info
from pymcu.hal.adc import AnalogPin as _AnalogPin


class Processor:
    """Microcontroller CPU information (CircuitPython microcontroller.Processor)."""

    @property
    def frequency(self) -> const[uint32]:
        """CPU frequency in Hz (compile-time constant on AVR)."""
        info = device_info()
        return info.frequency

    @property
    @warning("microcontroller.cpu.temperature uses the software floating-point runtime and the uncalibrated on-chip sensor (approximate, +/-10 C).")
    def temperature(self) -> float:
        """Die temperature in degrees Celsius, read from the internal sensor.

        Uses the on-chip temperature sensor (ADC channel 8, 1.1V reference) and
        the datasheet transfer function. The reading is uncalibrated and only
        approximate (typical accuracy +/-10 C without per-chip calibration).
        Requires a chip with an internal temperature sensor (ATmega328P family).
        """
        adc = _AnalogPin("TEMP")
        adc.start()
        raw: uint16 = adc.read()
        # Datasheet (ATmega328P, table 28-1): ~1 LSB/C, offset ~324.31 at 0 C,
        # slope ~1.22 LSB/C. T = (raw - 324.31) / 1.22  (soft-float).
        return (raw - 324.31) / 1.22

    @property
    @warning("microcontroller.cpu.voltage uses the software floating-point runtime (bandgap-vs-AVcc measurement).")
    def voltage(self) -> float:
        """Supply voltage (Vcc) in volts.

        Measures the internal 1.1V bandgap reference against AVcc and back-
        computes Vcc = 1.1 * 1024 / ADCraw (soft-float). Requires a chip that
        exposes the bandgap channel (ATmega328P family).
        """
        adc = _AnalogPin("VBG")
        adc.start()
        raw: uint16 = adc.read()
        return 1.1 * 1024.0 / raw

    @property
    def uid(self):
        """Unique chip identifier.

        CircuitPython returns a bytearray. The ATmega328P has no reliable
        factory-programmed unique serial number, so this returns an 8-tuple of
        zeros. Treat as unavailable on this target.
        """
        return (0, 0, 0, 0, 0, 0, 0, 0)


# CircuitPython exposes the processor as `microcontroller.cpu`.
cpu = Processor()


@inline
def reset():
    """Reset the microcontroller immediately.

    Implemented via the watchdog timer with the shortest timeout (~16 ms): the
    watchdog is armed in reset mode and the CPU spins until it fires, which
    restarts execution from the reset vector -- the bare-metal equivalent of
    CircuitPython's microcontroller.reset().
    """
    from pymcu.hal.watchdog import Watchdog as _Watchdog
    wd = _Watchdog(16)
    wd.enable()
    while True:
        pass


@inline
def delay_us(delay: uint32):
    """Busy-wait for the given number of microseconds (CircuitPython parity)."""
    from pymcu.time import delay_us as _delay_us
    _delay_us(delay)


class Pin:
    """Microcontroller pin reference (used by board pin definitions)."""
    pass

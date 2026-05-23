# CircuitPython-compatible microcontroller module for PyMCU
#
# Provides access to microcontroller-specific information and features.
#
# Usage:
#   import microcontroller
#   microcontroller.cpu.frequency  # CPU frequency in Hz
#   microcontroller.cpu.reset()    # Reset the MCU (not yet supported)
#
# Note: Most CircuitPython microcontroller features require runtime introspection
#       which is not available on bare-metal MCUs. This module provides compile-time
#       constants where possible.

from pymcu.types import uint8, uint32, inline, const
from pymcu.chips import device_info


class CPU:
    """Microcontroller CPU information."""

    @property
    def frequency(self) -> const[uint32]:
        """CPU frequency in Hz (compile-time constant)."""
        info = device_info()
        return info.frequency

    @property
    def temperature(self) -> uint8:
        """CPU temperature in Celsius (not supported on most AVR chips)."""
        raise NotImplementedError("CPU temperature sensor not available on this chip")

    @property
    def uid(self):
        """Unique ID tuple. AVR has no factory UID; returns 8-byte tuple of zeros."""
        return (0, 0, 0, 0, 0, 0, 0, 0)

    @property
    def voltage(self) -> uint8:
        """Supply voltage in volts (approximate). Returns 5 for standard 5V AVR boards."""
        return 5

    @inline
    def reset(self):
        """Reset the microcontroller. Not implemented via CPU object; use microcontroller.reset()."""
        raise NotImplementedError("Use microcontroller.reset() for MCU reset")


# Singleton instance
cpu = CPU()


@inline
def reset():
    """Module-level reset: triggers MCU reset via watchdog (mirrors CircuitPython)."""
    cpu.reset()


@inline
def delay_us(delay: uint32):
    """Busy-wait for the given number of microseconds."""
    from pymcu.time import delay_us as _delay_us
    _delay_us(delay)


class Pin:
    """Microcontroller pin reference (for board definitions)."""
    pass

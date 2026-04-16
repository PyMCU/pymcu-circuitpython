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

from pymcu.types import uint8, uint32, const
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

    def reset(self):
        """Reset the microcontroller (not yet supported)."""
        raise NotImplementedError("CPU reset not yet implemented")


# Singleton instance
cpu = CPU()


class Pin:
    """Microcontroller pin reference (for board definitions)."""
    # This is a placeholder for CircuitPython compatibility
    # Actual pin objects are created via board.D13, etc.
    pass

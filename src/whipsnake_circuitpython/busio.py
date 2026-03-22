# CircuitPython-compatible busio module for Whipsnake
#
# Provides UART, I2C, and SPI classes that mirror CircuitPython's busio API.
#
# UART usage:
#   import busio
#   import board
#   uart = busio.UART(board.TX, board.RX, baudrate=9600)
#   uart.write(b'Hello')
#
# I2C usage (context-manager style as per CircuitPython standard):
#   import busio
#   import board
#   i2c = busio.I2C(board.SCL, board.SDA)
#   with i2c:
#       i2c.write(0x68, 0x00)        # write one byte to device 0x68
#       val = i2c.read(0x68)         # read one byte from device 0x68
#   ok = i2c.try_lock()
#   i2c.unlock()
#
# SPI usage (context-manager style as per CircuitPython standard):
#   import busio
#   import board
#   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
#   with spi:
#       spi.write(0xAB)              # write one byte
#       val = spi.readinto()         # read one byte

from whipsnake.types import uint8, uint16, inline, const
from whipsnake.hal.uart import UART as _UART
from whipsnake.hal.i2c import I2C as _I2C
from whipsnake.hal.spi import SPI as _SPI


class UART:
    @inline
    def __init__(self, tx, rx, baudrate: uint16 = 9600):
        # tx/rx accepted for API compatibility; hardware pins are fixed on
        # ATmega328P (PD1=TX, PD0=RX) and configured inside _UART.__init__.
        self._hw = _UART(baudrate)

    @inline
    def write(self, data: uint8):
        self._hw.write(data)

    @inline
    def write_str(self, s: const[str]):
        self._hw.write_str(s)

    @inline
    def println(self, s: const[str]):
        self._hw.println(s)

    @inline
    def print_byte(self, value: uint8):
        self._hw.print_byte(value)

    @inline
    def read(self) -> uint8:
        return self._hw.read()


class I2C:
    """CircuitPython-compatible I2C bus.

    On AVR (ATmega328P) the pins are fixed: SCL=PC5 (A5), SDA=PC4 (A4).
    The scl and sda arguments are accepted for API compatibility but not used
    for hardware configuration.

    Usage (context-manager style):
        i2c = busio.I2C(board.SCL, board.SDA)
        with i2c:
            i2c.write(addr, data)

    Usage (lock style):
        i2c = busio.I2C(board.SCL, board.SDA)
        i2c.try_lock()
        i2c.write(addr, data)
        i2c.unlock()
    """

    @inline
    def __init__(self, scl, sda, frequency: uint32 = 100000):
        # scl/sda pin names accepted for API compatibility; hardware I2C on
        # ATmega328P uses fixed pins (PC5/PC4) configured by i2c_init().
        self._bus = _I2C()
        self._locked = 0

    @inline
    def try_lock(self) -> uint8:
        """Attempt to grab the I2C bus lock. Returns 1 on success."""
        if self._locked == 0:
            self._locked = 1
            return 1
        return 0

    @inline
    def unlock(self):
        """Release the I2C bus lock."""
        self._locked = 0

    @inline
    def scan(self) -> uint8:
        """Scan for devices; returns address of first device found (0 if none)."""
        addr: uint8 = 1
        while addr < 128:
            if self._bus.ping(addr):
                return addr
            addr = addr + 1
        return 0

    @inline
    def write(self, address: uint8, data: uint8) -> uint8:
        """Write one byte to a device. Returns 1 on ACK, 0 on NACK."""
        return self._bus.write_to(address, data)

    @inline
    def read(self, address: uint8) -> uint8:
        """Read one byte from a device."""
        return self._bus.read_from(address)

    @inline
    def writeto(self, address: uint8, data: uint8) -> uint8:
        """Alias for write() matching CircuitPython's writeto method."""
        return self._bus.write_to(address, data)

    @inline
    def readfrom_into(self, address: uint8) -> uint8:
        """Read one byte from address (CircuitPython-style name)."""
        return self._bus.read_from(address)

    @inline
    def __enter__(self):
        self._bus.start()

    @inline
    def __exit__(self):
        self._bus.stop()


class SPI:
    """CircuitPython-compatible SPI bus.

    On AVR (ATmega328P) the pins are fixed: SCK=PB5, MOSI=PB3, MISO=PB4.
    The clock, MOSI, MISO arguments are accepted for API compatibility.
    An optional cs (chip-select) pin can be specified.

    Usage (context-manager style):
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        with spi:
            spi.write(0xAB)
            val = spi.readinto()
    """

    @inline
    def __init__(self, clock, MOSI=None, MISO=None, cs: const[str] = ""):
        # clock/MOSI/MISO accepted for API compatibility; hardware SPI pins
        # are fixed on ATmega328P and configured by spi_init().
        self._bus = _SPI(cs)

    @inline
    def try_lock(self) -> uint8:
        """Attempt to grab the SPI bus lock. Always succeeds (returns 1)."""
        return 1

    @inline
    def unlock(self):
        """Release the SPI bus lock (no-op on bare metal)."""
        pass

    @inline
    def configure(self, baudrate: uint32 = 100000, polarity: uint8 = 0, phase: uint8 = 0, bits: uint8 = 8):
        """Configure SPI parameters (accepted for API compatibility; hardware uses fixed settings)."""
        pass

    @inline
    def write(self, data: uint8):
        """Write one byte to the SPI bus."""
        self._bus.transfer(data)

    @inline
    def readinto(self) -> uint8:
        """Read one byte from the SPI bus (sends 0xFF)."""
        return self._bus.transfer(0xFF)

    @inline
    def write_readinto(self, out: uint8) -> uint8:
        """Write and simultaneously read one byte (full-duplex)."""
        return self._bus.transfer(out)

    @inline
    def select(self):
        """Assert chip-select (pull CS low)."""
        self._bus.select()

    @inline
    def deselect(self):
        """Deassert chip-select (pull CS high)."""
        self._bus.deselect()

    @inline
    def __enter__(self):
        self._bus.select()

    @inline
    def __exit__(self):
        self._bus.deselect()

# CircuitPython-compatible bitbangio module for PyMCU
#
# The same buses as busio, driven in software on any two or three pins instead of the ones
# the peripheral is wired to. That is what it is for: an ATmega has one TWI and one SPI, and
# a board with two I2C sensors that answer at the same address needs a second bus.
#
#   import board, bitbangio
#
#   i2c = bitbangio.I2C(board.D2, board.D3)          # any two pins with pull-ups
#   i2c.writeto(0x68, bytes([0x6B, 0x00]))
#
#   spi = bitbangio.SPI(board.D5, MOSI=board.D6, MISO=board.D7)
#   spi.write(bytes([0x9F]))
#
# The API is busio's, method for method, because CircuitPython's is: a driver written
# against busio.I2C takes a bitbangio.I2C without knowing.
#
# Nothing here knows a pin's registers or how long a half-period is in cycles:
# pymcu.hal.softi2c and pymcu.hal.softspi answer both, and they are architecture-independent
# already, so this module works wherever pymcu.hal.gpio does.

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, inline, const
from pymcu.hal.gpio import Pin as _Pin
from pymcu.hal.softi2c import SoftI2C as _SoftI2C
from pymcu.hal.softspi import SoftSPI as _SoftSPI


class I2C:
    """A software I2C bus on any two pins.

    Both lines need external pull-ups: the bus is open-drain and neither pin is ever driven
    high, only released.

    `frequency` is the bit rate. It reaches the bus as a half-period in whole microseconds,
    so the rates actually available are 1 MHz, 500 kHz, 333 kHz, 250 kHz, 200 kHz, 166 kHz,
    142 kHz, 125 kHz, 111 kHz, 100 kHz and downwards; `frequency` reports the one in force.
    A software bus is slower than its half-period anyway, because the bit loop itself costs
    time, so treat the number as a ceiling.
    """

    @inline
    def __init__(self, scl, sda, *, frequency: uint32 = 400000, timeout: uint16 = 1):
        if frequency == 0:
            raise CompileError(
                "an I2C frequency of zero has no clock. Ask for a rate, or leave it out and "
                "take 400000, which is what CircuitPython's bitbangio defaults to.")
        if frequency > 1000000:
            raise CompileError(
                "this software I2C frequency is above what a whole-microsecond half-period "
                "can express: the fastest is 1000000. The bit loop costs time of its own on "
                "top of the half-period, so a software bus does not reach its nominal rate "
                "anyway. Ask for 1000000 or less, or use busio.I2C, which is the hardware "
                "peripheral.")
        self._scl = _Pin(scl, _Pin.OUT)
        self._sda = _Pin(sda, _Pin.OUT)
        self._frequency = frequency
        self._bus = _SoftI2C(self._scl, self._sda, uint8(500000 // frequency))
        self._bus.init()
        self._locked = 0

    @property
    def frequency(self) -> uint32:
        """The bit rate the bus is clocked at, which is not always the one asked for: the
        half-period is a whole number of microseconds."""
        return uint32(500000 // (500000 // self._frequency))

    @inline
    def try_lock(self) -> uint8:
        """Attempt to grab the bus lock. Returns 1 on success, 0 if already held."""
        if self._locked == 0:
            self._locked = 1
            return 1
        return 0

    @inline
    def unlock(self):
        """Release the bus lock."""
        self._locked = 0

    @inline
    def probe(self, address: uint8) -> uint8:
        """Return 1 if a device acknowledges at `address`, else 0."""
        return self._bus.ping(address)

    def scan(self):
        """Not available: there is no heap to return a list from."""
        raise CompileError(
            "bitbangio.I2C.scan() returns a list of the addresses that answered, and there "
            "is no heap here to build one on. Ask about one address at a time instead: "
            "`for a in range(8, 120): if i2c.probe(a): print(hex(a))` walks the same range "
            "and prints the same addresses.")

    @inline
    def writeto(self, address: uint8, buffer, *, start: uint16 = 0, end: uint16 = 65535):
        """Write `buffer[start:end]` to the device at `address`."""
        self._bus.start()
        self._bus.write((address << 1) & 0xFE)   # SLA+W
        for i, b in enumerate(buffer):
            if i >= start and i < end:
                self._bus.write(b)
        self._bus.stop()

    @inline
    def readfrom_into(self, address: uint8, buffer, *, start: uint16 = 0, end: uint16 = 65535):
        """Read into `buffer[start:end]` from the device at `address`.

        ACK is sent for every byte except the last, which is NACK'd, per the I2C protocol.
        """
        n: uint16 = 0
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                n = n + 1
        self._bus.start()
        self._bus.write((address << 1) | 1)      # SLA+R
        k: uint16 = 0
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                if k < n - 1:
                    buffer[i] = self._bus.read(1)
                else:
                    buffer[i] = self._bus.read(0)
                k = k + 1
        self._bus.stop()

    @inline
    def writeto_then_readfrom(self, address: uint8, out_buffer, in_buffer, *,
                              out_start: uint16 = 0, out_end: uint16 = 65535,
                              in_start: uint16 = 0, in_end: uint16 = 65535):
        """Write `out_buffer`, then (repeated START) read into `in_buffer`."""
        in_n: uint16 = 0
        for i, _ in enumerate(in_buffer):
            if i >= in_start and i < in_end:
                in_n = in_n + 1
        self._bus.start()
        self._bus.write((address << 1) & 0xFE)   # SLA+W
        for i, b in enumerate(out_buffer):
            if i >= out_start and i < out_end:
                self._bus.write(b)
        self._bus.start()                        # repeated START
        self._bus.write((address << 1) | 1)      # SLA+R
        k: uint16 = 0
        for i, _ in enumerate(in_buffer):
            if i >= in_start and i < in_end:
                if k < in_n - 1:
                    in_buffer[i] = self._bus.read(1)
                else:
                    in_buffer[i] = self._bus.read(0)
                k = k + 1
        self._bus.stop()

    @inline
    def deinit(self):
        """Release the bus lock and leave both lines idle high."""
        self._locked = 0
        self._bus.init()

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, *args):
        self.deinit()


class SPI:
    """A software SPI bus on any three pins.

    Chip-select is the caller's, through a `digitalio.DigitalInOut`, exactly as it is for
    `busio.SPI`.

    Mode 0 only. The bit loop clocks on the rising edge and samples before it, and there is
    no second loop here for the other three modes; `configure()` refuses a polarity or a
    phase of 1 and names `busio.SPI`, which is the hardware peripheral and does all four.
    """

    @inline
    def __init__(self, clock, MOSI=None, MISO=None):
        self._sck  = _Pin(clock, _Pin.OUT)
        self._mosi = _Pin(MOSI, _Pin.OUT)
        self._miso = _Pin(MISO, _Pin.IN)
        self._baudrate = 500000
        self._bus = _SoftSPI(self._sck, self._mosi, self._miso, 0, None, 500)

    @inline
    def try_lock(self) -> uint8:
        """Attempt to grab the bus lock. Always succeeds on bare metal (returns 1)."""
        return 1

    @inline
    def unlock(self):
        """Release the bus lock (no-op on bare metal)."""
        pass

    @inline
    def configure(self, *, baudrate: uint32 = 100000, polarity: uint8 = 0,
                  phase: uint8 = 0, bits: uint8 = 8):
        """Set the bit rate. Mode and frame size are fixed.

        The half-period is a whole number of microseconds, so the rates available are
        1 MHz, 500 kHz, 333 kHz and downwards; `frequency` reports the one in force.
        """
        if polarity != 0 or phase != 0:
            raise CompileError(
                "this software SPI clocks mode 0 and nothing else: the bit loop samples "
                "before the rising edge and shifts after it, and the other three modes are "
                "not written here. Use busio.SPI, which is the hardware peripheral and takes "
                "all four modes, or wire the device to it.")
        if bits != 8:
            raise CompileError(
                "this software SPI shifts 8 bits per frame. Pack the frame you need into "
                "whole bytes.")
        if baudrate == 0 or baudrate > 1000000:
            raise CompileError(
                "this software SPI bit rate is outside what a whole-microsecond half-period "
                "can express: the fastest is 1000000, and zero has no clock. The bit loop "
                "costs time of its own on top of the half-period, so a software bus does not "
                "reach its nominal rate anyway.")
        self._baudrate = baudrate
        self._bus.set_baudrate(uint16(baudrate // 1000))

    @property
    def frequency(self) -> uint32:
        """The bit rate the bus is clocked at, which is not always the one asked for."""
        return uint32(500000 // (500000 // self._baudrate))

    @inline
    def write(self, buf, *, start: uint16 = 0, end: uint16 = 65535):
        """Clock `buf[start:end]` out, discarding what comes back."""
        for i, b in enumerate(buf):
            if i >= start and i < end:
                self._bus.transfer(b)

    @inline
    def readinto(self, buffer, *, start: uint16 = 0, end: uint16 = 65535, write_value: uint8 = 0):
        """Read into `buffer[start:end]`, sending `write_value` for each byte."""
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                buffer[i] = self._bus.transfer(write_value)

    @inline
    def write_readinto(self, out_buffer, in_buffer, *, out_start: uint16 = 0,
                       out_end: uint16 = 65535, in_start: uint16 = 0, in_end: uint16 = 65535):
        """Full duplex: the two slices must be the same length, which SPI requires."""
        out_n: uint16 = 0
        for i, _ in enumerate(out_buffer):
            if i >= out_start and i < out_end:
                out_n = out_n + 1
        in_n: uint16 = 0
        for i, _ in enumerate(in_buffer):
            if i >= in_start and i < in_end:
                in_n = in_n + 1
        if out_n != in_n:
            raise CompileError(
                "the two buffers of a full-duplex SPI transfer must be the same length: one "
                "byte is clocked in for every byte clocked out, so a shorter read buffer "
                "would be written past its end. Make them the same size, or slice them to "
                "the same length with the start and end arguments.")
        for i, b in enumerate(out_buffer):
            if i >= out_start and i < out_end:
                in_buffer[i - out_start + in_start] = self._bus.transfer(b)

    @inline
    def deinit(self):
        """Release the bus (no-op on bare metal: the pins keep their direction)."""
        pass

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, *args):
        self.deinit()

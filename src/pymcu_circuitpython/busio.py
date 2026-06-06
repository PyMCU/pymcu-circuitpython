# CircuitPython-compatible busio module for PyMCU
#
# Provides UART, I2C and SPI classes that mirror CircuitPython's busio API,
# including its buffer-oriented (in-place) read/write methods.
#
# UART usage:
#   import busio, board
#   uart = busio.UART(board.TX, board.RX, baudrate=9600)
#   uart.write(b"Hello\r\n")
#   buf = bytearray(4)
#   n = uart.readinto(buf)
#
# I2C usage:
#   import busio, board
#   i2c = busio.I2C(board.SCL, board.SDA)
#   while not i2c.try_lock():
#       pass
#   i2c.writeto(0x68, bytes([0x00]))
#   data = bytearray(1)
#   i2c.readfrom_into(0x68, data)
#   i2c.unlock()
#
# SPI usage (chip-select is managed by the caller via digitalio, per CircuitPython):
#   import busio, board, digitalio
#   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
#   cs = digitalio.DigitalInOut(board.D10); cs.switch_to_output(value=True)
#   while not spi.try_lock():
#       pass
#   spi.configure(baudrate=1000000)
#   cs.value = False
#   spi.write(bytes([0x9F]))
#   cs.value = True
#   spi.unlock()
#
# On AVR the bus pins are fixed in hardware (ATmega328P: UART PD1/PD0,
# I2C PC5/PC4, SPI PB5/PB3/PB4); the pin arguments are accepted for API
# compatibility and validated by the underlying HAL.

from pymcu.types import uint8, uint16, uint32, inline, warning
from pymcu.hal.uart import UART as _UART
from pymcu.hal.i2c import I2C as _I2C
from pymcu.hal.spi import SPI as _SPI


class UART:
    class Parity:
        ODD  = 0
        EVEN = 1

    @inline
    def __init__(self, tx=None, rx=None, *, baudrate: uint16 = 9600, bits: uint8 = 8,
                 parity=None, stop: uint8 = 1, timeout: uint16 = 1,
                 receiver_buffer_size: uint16 = 64):
        # tx/rx accepted for API compatibility; hardware pins are fixed on AVR
        # (ATmega328P PD1=TX, PD0=RX) and configured inside _UART.__init__.
        self._hw       = _UART(baudrate)
        self._baudrate = baudrate
        self._timeout  = timeout

    @property
    def baudrate(self) -> uint16:
        """Current baud rate."""
        return self._baudrate

    @property
    def in_waiting(self) -> uint8:
        """Number of bytes available to read.

        On a polled hardware UART this reflects the RXC flag (0 or 1); for a
        true byte count, enable the interrupt-driven RX path in the HAL.
        """
        return self._hw.available()

    @property
    def timeout(self) -> uint16:
        """Read timeout (accepted for API compatibility).

        The bare-metal blocking read does not currently honour a timeout; the
        value is stored so code that gets/sets it compiles unchanged.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: uint16):
        self._timeout = value

    @inline
    def write(self, buf) -> uint16:
        """Write the bytes in `buf` to the bus; return the number written.

        `buf` may be a bytes/bytearray literal (unrolled at compile time) or a
        fixed-size uint8 array (loop). Matches CircuitPython UART.write(buf).
        """
        n: uint16 = 0
        for b in buf:
            self._hw.write(b)
            n = n + 1
        return n

    @inline
    def readinto(self, buf) -> uint16:
        """Read bytes into `buf` until it is full; return the number read."""
        n: uint16 = 0
        for i, _ in enumerate(buf):
            buf[i] = self._hw.read()
            n = n + 1
        return n

    @warning("busio.UART.read() cannot return a bytes object on bare metal (no heap); it is a no-op. Use readinto(buf) with a pre-allocated bytearray instead.")
    def read(self, nbytes=None):
        pass

    @warning("busio.UART.readline() cannot return a bytes object on bare metal (no heap); it is a no-op. Use readinto(buf) instead.")
    def readline(self):
        pass

    @inline
    def reset_input_buffer(self):
        """Discard any unread bytes in the receive buffer."""
        while self._hw.available():
            self._hw.read_nb()

    @inline
    def deinit(self):
        """Release the UART resource (no-op on bare metal)."""
        pass

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()


class I2C:
    """CircuitPython-compatible I2C bus controller.

    On AVR the pins are fixed (ATmega328P: SCL=PC5/A5, SDA=PC4/A4); scl/sda are
    accepted for API compatibility. All transfers use the caller's buffers, so
    no heap allocation is required.
    """

    @inline
    def __init__(self, scl, sda, *, frequency: uint32 = 100000, timeout: uint8 = 255):
        self._bus = _I2C()
        self._locked = 0

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

    @warning("busio.I2C.scan() cannot return a list on bare metal (no heap); it is a no-op. Use probe(address) in a loop over the address range instead.")
    def scan(self):
        pass

    @inline
    def writeto(self, address: uint8, buffer, start: uint8 = 0, end: uint8 = 0):
        """Write the bytes in `buffer` to the device at `address`.

        `buffer` may be a bytes/bytearray literal (unrolled) or a fixed-size
        uint8 array (loop). start/end are accepted for API compatibility; the
        whole buffer is sent.
        """
        self._bus.start()
        self._bus.write(address << 1)        # SLA+W
        for b in buffer:
            self._bus.write(b)
        self._bus.stop()

    @inline
    def readfrom_into(self, address: uint8, buffer, start: uint8 = 0, end: uint8 = 0):
        """Read len(buffer) bytes from the device at `address` into `buffer`.

        `buffer` must be a mutable fixed-size array. ACK is sent for every byte
        except the last, which is NACK'd, per the I2C protocol.
        """
        n: uint8 = 0
        for _ in buffer:
            n = n + 1
        self._bus.start()
        self._bus.write((address << 1) | 1)  # SLA+R
        for i, _ in enumerate(buffer):
            if i < n - 1:
                buffer[i] = self._bus.read_ack()
            else:
                buffer[i] = self._bus.read_nack()
        self._bus.stop()

    @inline
    def writeto_then_readfrom(self, address: uint8, out_buffer, in_buffer,
                              out_start: uint8 = 0, out_end: uint8 = 0,
                              in_start: uint8 = 0, in_end: uint8 = 0):
        """Write `out_buffer`, then (repeated START) read into `in_buffer`.

        `out_buffer` may be a literal (e.g. a register address) or an array;
        `in_buffer` must be a mutable fixed-size array to receive the data.
        """
        in_n: uint8 = 0
        for _ in in_buffer:
            in_n = in_n + 1
        self._bus.start()
        self._bus.write(address << 1)        # SLA+W
        for b in out_buffer:
            self._bus.write(b)
        self._bus.start()                    # repeated START
        self._bus.write((address << 1) | 1)  # SLA+R
        for i, _ in enumerate(in_buffer):
            if i < in_n - 1:
                in_buffer[i] = self._bus.read_ack()
            else:
                in_buffer[i] = self._bus.read_nack()
        self._bus.stop()

    @inline
    def deinit(self):
        """Release the I2C bus resource."""
        self._locked = 0

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()


class SPI:
    """CircuitPython-compatible SPI bus controller.

    On AVR the pins are fixed (ATmega328P: SCK=PB5, MOSI=PB3, MISO=PB4); clock/
    MOSI/MISO are accepted for API compatibility. Chip-select is managed by the
    caller with a digitalio.DigitalInOut, exactly as in CircuitPython.
    """

    @inline
    def __init__(self, clock, MOSI=None, MISO=None, half_duplex: uint8 = 0):
        self._bus = _SPI()
        self._frequency = 100000

    @inline
    def try_lock(self) -> uint8:
        """Attempt to grab the bus lock. Always succeeds on bare metal (returns 1)."""
        return 1

    @inline
    def unlock(self):
        """Release the bus lock (no-op on bare metal)."""
        pass

    @inline
    def configure(self, baudrate: uint32 = 100000, polarity: uint8 = 0,
                  phase: uint8 = 0, bits: uint8 = 8):
        """Configure SPI parameters. Accepted for API compatibility; the AVR
        hardware uses fixed settings, so only `baudrate` is recorded for the
        frequency property."""
        self._frequency = baudrate

    @property
    def frequency(self) -> uint32:
        """Configured SPI clock frequency in Hz."""
        return self._frequency

    @inline
    def write(self, buffer, start: uint16 = 0, end: uint16 = 0):
        """Write every byte in `buffer` to the bus (discarding read data)."""
        for b in buffer:
            self._bus.transfer(b)

    @inline
    def readinto(self, buffer, start: uint16 = 0, end: uint16 = 0, write_value: uint8 = 0):
        """Read len(buffer) bytes into `buffer`, sending `write_value` for each."""
        for i, _ in enumerate(buffer):
            buffer[i] = self._bus.transfer(write_value)

    @inline
    def write_readinto(self, out_buffer, in_buffer, out_start: uint16 = 0,
                       out_end: uint16 = 0, in_start: uint16 = 0, in_end: uint16 = 0):
        """Full-duplex: write `out_buffer` while reading into `in_buffer`."""
        for i, _ in enumerate(out_buffer):
            in_buffer[i] = self._bus.transfer(out_buffer[i])

    @inline
    def deinit(self):
        """Release the SPI bus resource (no-op on bare metal)."""
        pass

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

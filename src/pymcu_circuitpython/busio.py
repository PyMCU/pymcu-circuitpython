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
# Every parameter this module takes is carried to the HAL, which programs it or refuses it
# where the bus is constructed. Nothing here knows a register, a prescaler or a chip: the
# frame format, the bit rates and the buffer sizes are all the HAL's answers. A parameter
# that was accepted and dropped is the failure this module used to have -- a UART asked for
# 7E1 ran 8N1, a bus asked for 400 kHz ran at 100, and a display asked for mode 3 at 8 MHz
# ran mode 0 at 4 -- and every one of them was silent.
#
# On AVR the bus pins are fixed in hardware (ATmega328P: UART PD1/PD0, I2C PC5/PC4,
# SPI PB5/PB3/PB4); the pin arguments are accepted for API compatibility.

from pymcu.chips import __CHIP__
from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, int16, inline, const
from pymcu.hal.uart import UART as _UART
if __CHIP__.arch == "avr":
    from pymcu.hal.i2c import I2C as _I2C
    from pymcu.hal.spi import SPI as _SPI


# The parities, at module level. CircuitPython keeps them nested inside UART and spells them
# busio.UART.Parity.ODD, which is the shape PyMCU#319 cannot read: a constant two class names
# deep is refused where one deep works. UART.Parity below is the CircuitPython shape and will
# start working when that lands; busio.Parity is the spelling that compiles today.
#
# The numbers are the HAL's -- 0 none, 1 even, 2 odd on every architecture -- so a parity
# passed through needs no translation table. "No parity" is spelled None, as in CircuitPython.
class Parity:
    EVEN = 1
    ODD  = 2


class UART:
    class Parity:
        EVEN = 1
        ODD  = 2

    @inline
    def __init__(self, tx=None, rx=None, *, baudrate: uint16 = 9600, bits: uint8 = 8,
                 parity=None, stop: uint8 = 1, timeout: uint16 = 1000,
                 receiver_buffer_size: const[uint16] = 64):
        # tx/rx accepted for API compatibility; the hardware pins are fixed on AVR
        # (ATmega328P PD1=TX, PD0=RX) and configured inside _UART.__init__.
        #
        # bits, parity and stop reach the hardware now. A frame the part cannot send is
        # refused inside the HAL, where the register is, with the value named.
        #
        # parity=None is the CircuitPython spelling for no parity, and the HAL numbers no
        # parity 0. The translation is a match and not a local because the HAL needs the
        # value at compile time, and an annotated local is materialised and stops being one.
        match parity:
            case None:
                self._hw = _UART(baudrate, bits, 0, stop)
            case _:
                self._hw = _UART(baudrate, bits, parity, stop)
        self._baudrate = baudrate
        self._timeout  = timeout

        # CircuitPython's UART buffers received bytes, which is what makes in_waiting a
        # count and not a flag. The HAL has the ring and the interrupt that fills it; asking
        # for a buffer turns them on, and asking for one byte leaves the UART polled on the
        # hardware's own register.
        # A size bigger than the ring is refused inside the HAL, where the ring is: the
        # layer does not know how big it is and must not have to.
        self._buffered = 0
        if receiver_buffer_size > 1:
            self._buffered = 1
            self._hw.start_buffered_rx(receiver_buffer_size)

    @property
    def baudrate(self) -> uint16:
        """Current baud rate."""
        return self._baudrate

    @property
    def in_waiting(self) -> uint8:
        """How many bytes are waiting to be read.

        A real count when the UART is buffered. Unbuffered
        (`receiver_buffer_size=1`) it is 0 or 1, because the hardware holds one byte and has
        no count to give.
        """
        if self._buffered == 1:
            return self._hw.rx_count()
        return self._hw.available()

    @property
    def timeout(self) -> uint16:
        """Read timeout in milliseconds.

        CircuitPython spells it in seconds as a float; this layer has no float in a
        parameter default, so it is milliseconds here. `readinto` honours it: it used to
        block for ever, whatever this said.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: uint16):
        self._timeout = value

    @inline
    def write(self, buf) -> uint16:
        """Write the bytes in `buf` to the bus; return the number written.

        `buf` may be a bytes/bytearray literal (unrolled at compile time) or a fixed-size
        uint8 array (loop). Matches CircuitPython UART.write(buf).
        """
        n: uint16 = 0
        for b in buf:
            self._hw.write(b)
            n = n + 1
        return n

    @inline
    def readinto(self, buf) -> uint16:
        """Read bytes into `buf` until it is full or the timeout passes.

        Returns how many bytes were actually read, which is what CircuitPython returns and
        what tells a caller the read was short. It used to fill the buffer by blocking on
        each byte for ever, so a sensor that stopped answering hung the program.
        """
        n: uint16 = 0
        for i, _ in enumerate(buf):
            b: int16 = -1
            if self._buffered == 1:
                b = self._hw.rx_read_timeout(self._timeout)
            else:
                b = self._hw.read_timeout(self._timeout)
            if b < 0:
                return n
            buf[i] = b & 0xFF
            n = n + 1
        return n

    def read(self, nbytes=None):
        """Not available: there is no heap to return a bytes object from."""
        raise CompileError(
            "busio.UART.read() returns a bytes object, and there is no heap here to build "
            "one on. Read into a buffer you own instead: allocate `buf = bytearray(n)` once "
            "and call `uart.readinto(buf)`, which returns how many bytes it got. It used to "
            "compile to nothing and hand back a value that was never read.")

    def readline(self):
        """Not available: there is no heap to return a bytes object from."""
        raise CompileError(
            "busio.UART.readline() returns a bytes object, and there is no heap here to "
            "build one on. Read into a buffer you own a byte at a time and stop at the "
            "newline yourself, or use pymcu.hal.uart's read_line(buf, max_len), which fills "
            "a buffer you allocated and returns the length. It used to compile to nothing.")

    @inline
    def reset_input_buffer(self):
        """Discard any unread bytes in the receive buffer."""
        if self._buffered == 1:
            while self._hw.rx_count() != 0:
                self._hw.rx_read()
        else:
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
        # frequency reaches the bit-rate register now. A rate the hardware cannot clock is
        # refused inside the HAL with the reachable range named; it used to be dropped here
        # and the bus ran at 100 kHz whatever the program asked for.
        self._bus = _I2C(0, 0, frequency)
        self._locked = 0

    @property
    def frequency(self) -> uint32:
        """The SCL rate the bus actually clocks, which is not always the one asked for: the
        bit-rate register is an integer."""
        return self._bus.frequency()

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
            "busio.I2C.scan() returns a list of the addresses that answered, and there is "
            "no heap here to build one on. Ask about one address at a time instead: "
            "`for a in range(8, 120): if i2c.probe(a): print(hex(a))` walks the same range "
            "and prints the same addresses. It used to compile to nothing, so the scan "
            "found nothing and said nothing.")

    @inline
    def writeto(self, address: uint8, buffer, start: uint16 = 0, end: uint16 = 65535):
        """Write `buffer[start:end]` to the device at `address`.

        start and end slice the buffer, as they do in CircuitPython. They used to be
        accepted and the whole buffer sent, so a program writing one register out of a
        packet wrote the packet. At their defaults the bounds fold away and this is the
        same loop it always was.
        """
        self._bus.start()
        self._bus.write(address << 1)        # SLA+W
        for i, b in enumerate(buffer):
            if i >= start and i < end:
                self._bus.write(b)
        self._bus.stop()

    @inline
    def readfrom_into(self, address: uint8, buffer, start: uint16 = 0, end: uint16 = 65535):
        """Read into `buffer[start:end]` from the device at `address`.

        ACK is sent for every byte except the last, which is NACK'd, per the I2C protocol.
        """
        n: uint16 = 0
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                n = n + 1
        self._bus.start()
        self._bus.write((address << 1) | 1)  # SLA+R
        k: uint16 = 0
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                if k < n - 1:
                    buffer[i] = self._bus.read_ack()
                else:
                    buffer[i] = self._bus.read_nack()
                k = k + 1
        self._bus.stop()

    @inline
    def writeto_then_readfrom(self, address: uint8, out_buffer, in_buffer,
                              out_start: uint16 = 0, out_end: uint16 = 65535,
                              in_start: uint16 = 0, in_end: uint16 = 65535):
        """Write `out_buffer[out_start:out_end]`, then (repeated START) read into
        `in_buffer[in_start:in_end]`."""
        in_n: uint16 = 0
        for i, _ in enumerate(in_buffer):
            if i >= in_start and i < in_end:
                in_n = in_n + 1
        self._bus.start()
        self._bus.write(address << 1)        # SLA+W
        for i, b in enumerate(out_buffer):
            if i >= out_start and i < out_end:
                self._bus.write(b)
        self._bus.start()                    # repeated START
        self._bus.write((address << 1) | 1)  # SLA+R
        k: uint16 = 0
        for i, _ in enumerate(in_buffer):
            if i >= in_start and i < in_end:
                if k < in_n - 1:
                    in_buffer[i] = self._bus.read_ack()
                else:
                    in_buffer[i] = self._bus.read_nack()
                k = k + 1
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
        """Program the clock rate, the mode and the frame size.

        It used to record `baudrate` and reprogram nothing, so a display asked for mode 3
        at 8 MHz ran mode 0 at 4 MHz. polarity and phase are the two bits that name the SPI
        mode; the HAL refuses anything but 0 or 1 for each.
        """
        if bits != 8:
            raise CompileError(
                "this SPI bus shifts 8 bits per frame and the hardware has no other frame "
                "size. Drop the bits argument, or pack the frame you need into whole bytes.")
        self._bus.configure(baudrate, polarity, phase)

    @property
    def frequency(self) -> uint32:
        """The clock rate the bus actually runs at, which is not always the one asked for:
        the dividers are powers of two."""
        return self._bus.frequency()

    @inline
    def write(self, buffer, start: uint16 = 0, end: uint16 = 65535):
        """Write `buffer[start:end]` to the bus (discarding read data)."""
        for i, b in enumerate(buffer):
            if i >= start and i < end:
                self._bus.transfer(b)

    @inline
    def readinto(self, buffer, start: uint16 = 0, end: uint16 = 65535, write_value: uint8 = 0):
        """Read into `buffer[start:end]`, sending `write_value` for each byte."""
        for i, _ in enumerate(buffer):
            if i >= start and i < end:
                buffer[i] = self._bus.transfer(write_value)

    @inline
    def write_readinto(self, out_buffer, in_buffer, out_start: uint16 = 0,
                       out_end: uint16 = 65535, in_start: uint16 = 0, in_end: uint16 = 65535):
        """Full-duplex: write `out_buffer` while reading into `in_buffer`.

        The two slices must be the same length, which SPI requires: one byte goes out for
        every byte that comes in. It used to index `in_buffer` with `out_buffer`'s index and
        check nothing, so a shorter `in_buffer` was written past its end.
        """
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
                "would be written past its end and a longer one left part unfilled. Make "
                "them the same size, or slice them to the same length with the start and "
                "end arguments.")
        for i, b in enumerate(out_buffer):
            if i >= out_start and i < out_end:
                in_buffer[i - out_start + in_start] = self._bus.transfer(b)

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

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

from typing import Optional

from pymcu.chips import __CHIP__
from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, int16, inline, const
from pymcu.hal.uart import UART as _UART
if __CHIP__.arch == "avr":
    from pymcu.hal.i2c import I2C as _I2C
    from pymcu.hal.avr.i2c.avr import (
        i2c_start as _hal_i2c_start, i2c_stop as _hal_i2c_stop,
        i2c_write as _hal_i2c_write,
        i2c_read_ack as _hal_i2c_read_ack, i2c_read_nack as _hal_i2c_read_nack,
    )
    from pymcu.hal.spi import SPI as _SPI
else:
    # On the ARM ports the UART HAL has no timed read: readinto polls the RX flag
    # against the free-running microsecond TIMER instead (no init needed there).
    from pymcu.time import micros as _micros


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


@inline
def _timeout_ms(timeout) -> uint16:
    # CircuitPython coerces the timeout with mp_obj_get_float, so EVERY numeric
    # spelling is seconds: timeout=1 is one second, timeout=0.1 is 100 ms, and
    # the upstream default 1.0 reads back as 1.0. The value is stored as uint16
    # milliseconds, which is what the two HALs' timed reads take -- so a value
    # past 65.535 s (or a negative one) cannot be represented and is refused.
    if timeout is None:
        raise CompileError(
            "busio.UART: timeout is a number of seconds; None is not one. "
            "Pass a float or an int.")
    if isinstance(timeout, int):
        # An int can only reach the field when it fits: 66 s is already past
        # 65535 ms, so 65 is the largest whole number that compiles.
        if timeout < 0 or timeout > 65:
            raise CompileError(
                "busio.UART: timeout is a number of seconds -- this layer holds "
                "it as uint16 milliseconds, so it cannot go past 65.535 s.")
        return uint16(timeout * 1000.0 + 0.5)
    if timeout < 0.0 or timeout > 65.535:
        raise CompileError(
            "busio.UART: timeout is a number of seconds -- this layer holds it "
            "as uint16 milliseconds, so it cannot go past 65.535 s.")
    return uint16(timeout * 1000.0 + 0.5)


@inline
def _rp_uart_tx_id(pin) -> int16:
    # The peripheral's own mux table (CircuitPython's common-hal busio.UART
    # derives the instance from the pins the same way): TX pads sit at
    # (pin & 3) == 0 on the RP2040 and at every even pin on the RP2350, and the
    # UART id is bit 3 of pin + 4 in both. -1 means the pin is no TX pad at all.
    if __CHIP__.name == "rp2350":
        if pin < 0 or pin > 47 or pin & 1:
            return -1
    elif pin < 0 or pin > 29 or pin & 3:
        return -1
    return (pin + 4) >> 3 & 1


@inline
def _rp_uart_rx_id(pin) -> int16:
    # The RX half of the same table: (pin & 3) == 1 on the RP2040, every odd
    # pin on the RP2350.
    if __CHIP__.name == "rp2350":
        if pin < 0 or pin > 47 or (pin & 1) == 0:
            return -1
    elif pin < 0 or pin > 29 or (pin & 3) != 1:
        return -1
    return (pin + 4) >> 3 & 1


class UART:
    class Parity:
        EVEN = 1
        ODD  = 2

    @inline
    def __init__(self, tx=None, rx=None, *, baudrate: uint32 = 9600, bits: uint8 = 8,
                 parity=None, stop: uint8 = 1, timeout: const = 1.0,
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
        if __CHIP__.arch != "avr":
            # CircuitPython refuses a UART with neither pad; this port must refuse
            # either missing one, too: the rp UART HAL routes exactly the pads it is
            # handed and can wire no tx-only or rx-only half, so a None can never fall
            # through to GP0/GP1 defaults the caller never named.
            if tx is None and rx is None:
                raise CompileError(
                    "busio.UART: tx and rx cannot both be None -- at least one pad "
                    "must be wired (CircuitPython refuses this the same way).")
            if tx is None or rx is None:
                raise CompileError(
                    "busio.UART: this chip's UART HAL routes both the tx and the rx "
                    "pad it is given; a tx-only or rx-only UART is not expressible "
                    "here -- pass both pins.")
            # Which UART the pair belongs to comes from the chip's mux table,
            # exactly like CircuitPython's common-hal does. This HAL drives
            # UART0 only, so a pair that is real on the chip but routes to
            # UART1 (GP4/GP5 on an RP2040) is refused -- silently muxing those
            # pads while writing the UART0 registers would drive nothing, which
            # is what happened here.
            if _rp_uart_tx_id(tx) < 0:
                raise CompileError(
                    "busio.UART: tx is not a UART transmit pad on this chip "
                    "(RP2040 TX pads: GP0, GP4, GP8, GP12, GP16, GP20, GP24, "
                    "GP28).")
            if _rp_uart_rx_id(rx) < 0:
                raise CompileError(
                    "busio.UART: rx is not a UART receive pad on this chip "
                    "(RP2040 RX pads: GP1, GP5, GP9, GP13, GP17, GP21, GP25, "
                    "GP29).")
            if _rp_uart_tx_id(tx) != _rp_uart_rx_id(rx):
                raise CompileError(
                    "busio.UART: tx and rx belong to different UARTs; a pair "
                    "must sit on the same peripheral.")
            if _rp_uart_tx_id(tx) != 0:
                raise CompileError(
                    "busio.UART: these pads belong to UART1 and this chip's HAL "
                    "drives UART0 only -- pick a UART0 pair (RP2040: GP0/GP1, "
                    "GP12/GP13, GP16/GP17, GP28/GP29) or a HAL that programs "
                    "UART1.")
        match parity:
            case None:
                if __CHIP__.arch == "avr":
                    self._hw = _UART(baudrate, bits, 0, stop)
                else:
                    # The RP2040/RP2350 UART HAL takes the pads in second and third
                    # place and routes them.
                    self._hw = _UART(baudrate, tx, rx, bits, 0, stop)
            case _:
                if __CHIP__.arch == "avr":
                    self._hw = _UART(baudrate, bits, parity, stop)
                else:
                    self._hw = _UART(baudrate, tx, rx, bits, parity, stop)
        self._baudrate = baudrate
        self._timeout  = _timeout_ms(timeout)

        # CircuitPython's UART buffers received bytes, which is what makes in_waiting a
        # count and not a flag. The HAL has the ring and the interrupt that fills it; asking
        # for a buffer turns them on, and asking for one byte leaves the UART polled on the
        # hardware's own register.
        # A size bigger than the ring is refused inside the HAL, where the ring is: the
        # layer does not know how big it is and must not have to.
        self._buffered = 0
        if receiver_buffer_size > 1:
            if __CHIP__.arch == "avr":
                self._buffered = 1
                self._hw.start_buffered_rx(receiver_buffer_size)
            elif receiver_buffer_size > 32:
                # On RP the receive buffer is the PL011's own 32-entry hardware
                # FIFO -- there is no interrupt-driven ring to deepen it, so a
                # request for more than 32 bytes cannot be honoured. Anything up
                # to 32 is already true: bytes that land while the program is
                # elsewhere sit in the FIFO until read.
                raise CompileError(
                    "busio.UART on this chip buffers received bytes in the UART's "
                    "32-entry hardware FIFO -- the interrupt-driven ring that would "
                    "deepen it exists only on the AVR HAL. Pass a "
                    "receiver_buffer_size of 32 or less.")

    @property
    def baudrate(self) -> uint32:
        """Current baud rate."""
        return self._baudrate

    @property
    def in_waiting(self) -> uint8:
        """How many bytes are waiting to be read.

        A real count when the UART is buffered. Unbuffered
        (`receiver_buffer_size=1`) it is 0 or 1, because the hardware holds one byte and has
        no count to give.
        """
        if __CHIP__.arch == "avr":
            if self._buffered == 1:
                return self._hw.rx_count()
            return self._hw.available()
        else:
            # The rp UART FIFO reports only empty-or-not -- no count. Answering
            # 0-or-1 as if it were a count would report 1 for two queued bytes,
            # a number that is false, so the property refuses on this port.
            raise CompileError(
                "busio.UART.in_waiting is a byte count and this chip's UART FIFO "
                "reports only empty-or-not -- it cannot count. Poll readinto() "
                "instead; it reports how many bytes it actually got.")

    @property
    def timeout(self) -> float:
        """Read timeout in seconds (a float, as in CircuitPython).

        Stored as uint16 milliseconds; every numeric spelling is seconds
        (upstream coerces with mp_obj_get_float), so `timeout = 1` is one
        second and `timeout = 0.1` is 100 ms.
        """
        return self._timeout / 1000.0

    @timeout.setter
    def timeout(self, value: const):
        # The same seconds spelling the constructor takes (an int is seconds
        # too, like upstream). The value must be a compile-time constant so a
        # number beyond the field's reach is refused here, at compile time,
        # instead of trapping at runtime.
        self._timeout = _timeout_ms(value)

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
    def readinto(self, buf) -> Optional[uint16]:
        """Read bytes into `buf` until it is full or the timeout passes.

        Returns how many bytes were actually read, which is what tells a caller the
        read was short -- None when the timeout ran out before the first byte, as
        CircuitPython returns. The AVR port still answers 0 there; only ports whose
        inline expansion can carry the Optional answer None (the ARM ones do).
        """
        n: uint16 = 0
        for i, _ in enumerate(buf):
            if __CHIP__.arch == "avr":
                b: int16 = -1
                if self._buffered == 1:
                    b = self._hw.rx_read_timeout(self._timeout)
                else:
                    b = self._hw.read_timeout(self._timeout)
                if b < 0:
                    return n
                buf[i] = b & 0xFF
            else:
                # This port's UART HAL has no timed read (and no RX ring, so
                # _buffered is always 0 here). Poll the RX-not-empty flag against
                # the free-running microsecond TIMER until the byte lands or the
                # timeout passes; the unsigned difference wraps safely.
                start_us: uint32 = _micros()
                while self._hw.available() == 0:
                    if _micros() - start_us >= uint32(self._timeout) * 1000:
                        if n == 0:
                            return None
                        return n
                buf[i] = self._hw.read()
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
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()


# The transfer bodies of busio.I2C live here as module-level shared subroutines,
# compiled once: the methods below are thin @inline wrappers that fold the
# buffer's compile-time length into the slice bounds and call in. The buffer
# arrives as a pointer and the bounds as ordinary arguments, so the START,
# address and data ACK checks exist once in the image -- expanded inline they
# cost a hundred bytes a copy, and a driver like the SSD1306's carries fifty.
#
# Two shapes per transfer: the full-buffer form takes the byte count alone and
# drops the slice start (always zero) off the call, while the windowed form is
# compiled only when a caller actually slices -- a program that never does pays
# nothing for it. The raise paths share the _i2c_fail_* stubs so the message
# store and error return are emitted once per failure kind, not once per site.
# The bodies call the HAL primitives the module import binds for the chip.
# Ports that bind nothing (everything but AVR today) cannot compile them at
# all -- the primitives are undefined names there -- so each body sits behind
# the same arch check the import does and folds away unused on those ports,
# where the busio classes refuse construction instead.
def _i2c_fail_io():
    if __CHIP__.arch == "avr":
        _hal_i2c_stop()
        raise OSError("[Errno 5] Input/output error")


def _i2c_fail_nodev():
    if __CHIP__.arch == "avr":
        _hal_i2c_stop()
        raise OSError("[Errno 19] No such device")


def _i2c_writeto(address: uint8, buffer, n: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write(address << 1) != _I2C.SLA_ACK:       # SLA+W
            _i2c_fail_nodev()
        k: uint16 = 0
        while k < n:
            if _hal_i2c_write(buffer[k]) != _I2C.DATA_ACK:
                _i2c_fail_io()
            k = k + 1
        _hal_i2c_stop()


def _i2c_writeto_window(address: uint8, buffer, start: uint16, end: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write(address << 1) != _I2C.SLA_ACK:       # SLA+W
            _i2c_fail_nodev()
        i: uint16 = start
        while i < end:
            if _hal_i2c_write(buffer[i]) != _I2C.DATA_ACK:
                _i2c_fail_io()
            i = i + 1
        _hal_i2c_stop()


def _i2c_readfrom(address: uint8, buffer, n: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write((address << 1) | 1) != _I2C.SLA_R_ACK:   # SLA+R
            _i2c_fail_nodev()
        if n > 0:
            last: uint16 = n - 1
            k: uint16 = 0
            while k < last:
                buffer[k] = _hal_i2c_read_ack()
                k = k + 1
            buffer[last] = _hal_i2c_read_nack()
        _hal_i2c_stop()


def _i2c_readfrom_window(address: uint8, buffer, start: uint16, n: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write((address << 1) | 1) != _I2C.SLA_R_ACK:   # SLA+R
            _i2c_fail_nodev()
        if n > 0:
            last: uint16 = n - 1
            k: uint16 = 0
            while k < last:
                buffer[start + k] = _hal_i2c_read_ack()
                k = k + 1
            buffer[start + last] = _hal_i2c_read_nack()
        _hal_i2c_stop()


def _i2c_writeto_then_readfrom(address: uint8, out_buffer, out_n: uint16,
                               in_buffer, in_n: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write(address << 1) != _I2C.SLA_ACK:       # SLA+W
            _i2c_fail_nodev()
        i: uint16 = 0
        while i < out_n:
            if _hal_i2c_write(out_buffer[i]) != _I2C.DATA_ACK:
                _i2c_fail_io()
            i = i + 1
        st = _hal_i2c_start()                                  # repeated START
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write((address << 1) | 1) != _I2C.SLA_R_ACK:   # SLA+R
            _i2c_fail_nodev()
        if in_n > 0:
            last: uint16 = in_n - 1
            k: uint16 = 0
            while k < last:
                in_buffer[k] = _hal_i2c_read_ack()
                k = k + 1
            in_buffer[last] = _hal_i2c_read_nack()
        _hal_i2c_stop()


def _i2c_writeto_then_readfrom_window(address: uint8, out_buffer,
                                      out_start: uint16, out_end: uint16,
                                      in_buffer, in_start: uint16,
                                      in_n: uint16):
    if __CHIP__.arch == "avr":
        st: uint8 = _hal_i2c_start()
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write(address << 1) != _I2C.SLA_ACK:       # SLA+W
            _i2c_fail_nodev()
        i: uint16 = out_start
        while i < out_end:
            if _hal_i2c_write(out_buffer[i]) != _I2C.DATA_ACK:
                _i2c_fail_io()
            i = i + 1
        st = _hal_i2c_start()                                  # repeated START
        if st != _I2C.START and st != _I2C.RESTART:
            _i2c_fail_io()
        if _hal_i2c_write((address << 1) | 1) != _I2C.SLA_R_ACK:   # SLA+R
            _i2c_fail_nodev()
        if in_n > 0:
            last: uint16 = in_n - 1
            k: uint16 = 0
            while k < last:
                in_buffer[in_start + k] = _hal_i2c_read_ack()
                k = k + 1
            in_buffer[in_start + last] = _hal_i2c_read_nack()
        _hal_i2c_stop()


class I2C:
    """CircuitPython-compatible I2C bus controller.

    On AVR the pins are fixed (ATmega328P: SCL=PC5/A5, SDA=PC4/A4); scl/sda are
    accepted for API compatibility. All transfers use the caller's buffers, so
    no heap allocation is required.
    """

    @inline
    def __init__(self, scl, sda, *, frequency: uint32 = 100000, timeout: uint8 = 255):
        if __CHIP__.arch == "avr":
            # frequency reaches the bit-rate register now. A rate the hardware cannot
            # clock is refused inside the HAL with the reachable range named; it used
            # to be dropped here and the bus ran at 100 kHz whatever the program asked.
            self._bus = _I2C(0, 0, frequency)
            # CircuitPython checks the wiring: with the pull-ups the HAL just enabled
            # holding the bus up and the TWI not driving anything until the first
            # START, both lines read at the pins must be high. A line still low is a
            # bus with nothing pulling it up, and refusing here is the message
            # shared-module busio I2C raises on every port that keeps
            # CIRCUITPY_REQUIRE_I2C_PULLUPS. The text is that port's own.
            if self._bus.lines_high() == 0:
                raise RuntimeError("No pull up found on SDA or SCL; check your wiring")
            self._locked = 0
        else:
            # No silent wrong bus: the transactions below are byte-level TWI
            # primitives, and this port's I2C HAL does not offer that shape (the
            # rp2040/rp2350 one is transaction-level and writes only, so
            # readfrom_into could never run on it at all).
            raise CompileError(
                "busio.I2C drives the controller a byte at a time -- start, address, "
                "write, read with ack/nack, stop -- which only the AVR HAL exposes "
                "today. On this chip bitbangio.I2C bit-bangs the same CircuitPython "
                "API on any two pins.")

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
    def writeto(self, address: uint8, buffer, *, start: uint16 = 0, end: uint16 = 65535):
        """Write `buffer[start:end]` to the device at `address`.

        start and end slice the buffer, as they do in CircuitPython. They used to be
        accepted and the whole buffer sent, so a program writing one register out of a
        packet wrote the packet. At their defaults the bounds fold away and this is the
        same loop it always was.

        A NACK raises OSError, as CircuitPython does: [Errno 19] No such device when
        the address goes unanswered, [Errno 5] Input/output error when the START or a
        data byte fails. That is what adafruit_bus_device.I2CDevice catches to report
        "No I2C device at address"; it used to be ignored, so a dark display looked
        exactly like a working one.

        The body lives in `_i2c_writeto` so the checks compile once; this wrapper
        folds the buffer's length into `end` where the caller can still see it.
        The length goes straight into the call as `len(buffer)` -- a compile-time
        constant -- rather than through a `limit` local the conditional clamp would
        rebind, which would keep the argument a runtime variable at the marshal.
        """
        if end < len(buffer):
            _i2c_writeto_window(address, buffer, start, end)
        elif start == 0:
            _i2c_writeto(address, buffer, len(buffer))
        else:
            _i2c_writeto_window(address, buffer, start, len(buffer))

    @inline
    def readfrom_into(self, address: uint8, buffer, *, start: uint16 = 0, end: uint16 = 65535):
        """Read into `buffer[start:end]` from the device at `address`.

        ACK is sent for every byte except the last, which is NACK'd, per the I2C protocol.

        Raises OSError like writeto does: [Errno 19] when the address is NACK'd,
        [Errno 5] when the START fails.
        """
        if start == 0:
            # The common read fills the buffer from offset 0; `len(buffer)` reaches the
            # call as a compile-time constant instead of a rebound local.
            if end < len(buffer):
                _i2c_readfrom(address, buffer, end)
            else:
                _i2c_readfrom(address, buffer, len(buffer))
        else:
            limit: uint16 = len(buffer)
            if end < limit:
                limit = end
            n: uint16 = 0
            if start < limit:
                n = limit - start
            _i2c_readfrom_window(address, buffer, start, n)

    @inline
    def writeto_then_readfrom(self, address: uint8, out_buffer, in_buffer, *,
                              out_start: uint16 = 0, out_end: uint16 = 65535,
                              in_start: uint16 = 0, in_end: uint16 = 65535):
        """Write `out_buffer[out_start:out_end]`, then (repeated START) read into
        `in_buffer[in_start:in_end]`.

        Raises OSError like writeto/readfrom_into do."""
        out_limit: uint16 = len(out_buffer)
        if out_end < out_limit:
            out_limit = out_end
        out_n: uint16 = 0
        if out_start < out_limit:
            out_n = out_limit - out_start
        in_limit: uint16 = len(in_buffer)
        if in_end < in_limit:
            in_limit = in_end
        in_n: uint16 = 0
        if in_start < in_limit:
            in_n = in_limit - in_start
        if out_start == 0 and in_start == 0:
            _i2c_writeto_then_readfrom(address, out_buffer, out_n, in_buffer, in_n)
        else:
            _i2c_writeto_then_readfrom_window(address, out_buffer, out_start,
                                              out_limit, in_buffer, in_start, in_n)

    @inline
    def deinit(self):
        """Release the I2C bus resource."""
        self._locked = 0

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()


class SPI:
    """CircuitPython-compatible SPI bus controller.

    On AVR the pins are fixed (ATmega328P: SCK=PB5, MOSI=PB3, MISO=PB4); clock/
    MOSI/MISO are accepted for API compatibility. Chip-select is managed by the
    caller with a digitalio.DigitalInOut, exactly as in CircuitPython.
    """

    @inline
    def __init__(self, clock, MOSI=None, MISO=None, half_duplex: uint8 = 0):
        if __CHIP__.arch == "avr":
            self._bus = _SPI()
        else:
            # busio.SPI reconfigures a bus after taking its lock (configure()
            # programs rate/mode/bits on a bus built earlier); this port's SPI
            # HAL fixes pins, mode and rate at construction and has no
            # configure(), so the busio contract cannot sit on it.
            raise CompileError(
                "busio.SPI needs a hardware bus it can reconfigure after locking "
                "(configure() programs baudrate, polarity and phase), which only "
                "the AVR HAL exposes today. On this chip bitbangio.SPI bit-bangs "
                "the same CircuitPython API on any pins.")

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
    def write(self, buffer, *, start: uint16 = 0, end: uint16 = 65535):
        """Write `buffer[start:end]` to the bus (discarding read data)."""
        for i, b in enumerate(buffer):
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
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deinit()

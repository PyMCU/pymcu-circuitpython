"""busio: UART/I2C/SPI buffer-based API (CircuitPython parity).

The theme of these tests is that a parameter reaches the hardware. busio used to accept
bits, parity, stop, frequency, polarity and phase and drop every one of them, so a UART
asked for 7E1 ran 8N1 and a bus asked for 400 kHz ran at 100, silently.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.busio import UART, I2C, SPI, Parity


def test_uart_baudrate():
    u = UART(None, None, baudrate=19200)
    assert u.baudrate == 19200


def test_uart_write_buffer_returns_count():
    u = UART(None, None, baudrate=9600)
    assert u.write(b"Hello") == 5


def test_uart_frame_reaches_the_hardware():
    u = UART(None, None, baudrate=9600, bits=7, parity=Parity.EVEN, stop=2)
    assert (u._hw.bits, u._hw.parity, u._hw.stop) == (7, 1, 2)


def test_no_parity_is_spelled_none_and_arrives_as_zero():
    u = UART(None, None, baudrate=9600)
    assert u._hw.parity == 0


def test_uart_parity_numbers_are_the_hals():
    # 0 none, 1 even, 2 odd on every architecture, so nothing has to translate them.
    assert (Parity.EVEN, Parity.ODD) == (1, 2)
    assert (UART.Parity.EVEN, UART.Parity.ODD) == (1, 2)


def test_readinto_returns_what_it_got_instead_of_blocking():
    # It used to block on every byte for ever, so a sensor that stopped answering hung the
    # program whatever timeout the constructor was given.
    u = UART(None, None, baudrate=9600)
    u._hw._ring.extend([0x41, 0x42])
    buf = bytearray(4)
    assert u.readinto(buf) == 2
    assert buf[0] == 0x41 and buf[1] == 0x42


def test_readinto_with_nothing_to_read_returns_zero():
    u = UART(None, None, baudrate=9600)
    assert u.readinto(bytearray(4)) == 0


def test_in_waiting_is_a_count_when_buffered():
    # It used to be the receive-complete flag: 0 or 1 however many bytes had arrived.
    u = UART(None, None, baudrate=9600)
    u._hw._ring.extend([1, 2, 3])
    assert u.in_waiting == 3


def test_a_buffer_bigger_than_the_ring_is_refused():
    with pytest.raises(CompileError):
        UART(None, None, baudrate=9600, receiver_buffer_size=256)


def test_read_and_readline_say_what_to_use_instead():
    u = UART(None, None, baudrate=9600)
    # They used to be @warning no-ops: they compiled to nothing and handed back a value
    # that was never read.
    with pytest.raises(CompileError) as e:
        u.read(4)
    assert "readinto" in str(e.value)
    with pytest.raises(CompileError) as e:
        u.readline()
    assert "buffer" in str(e.value)


def test_i2c_lock():
    i2c = I2C(None, None)
    assert i2c.try_lock() == 1
    assert i2c.try_lock() == 0   # already held
    i2c.unlock()
    assert i2c.try_lock() == 1


def test_i2c_frequency_reaches_the_bus():
    assert I2C(None, None, frequency=400000).frequency == 400000
    assert I2C(None, None).frequency == 100000


def test_i2c_scan_says_what_to_use_instead():
    # It used to be a @warning no-op, so the scan found nothing and said nothing.
    with pytest.raises(CompileError) as e:
        I2C(None, None).scan()
    assert "probe" in str(e.value)


def test_i2c_probe_and_writeto():
    i2c = I2C(None, None)
    i2c.probe(0x68)
    i2c.writeto(0x68, b"\x00\x01")
    rx = bytearray(2)
    i2c.readfrom_into(0x68, rx)


def test_i2c_no_legacy_single_byte_api():
    # Strict parity: write/read single-byte helpers replaced by writeto/readfrom_into.
    i2c = I2C(None, None)
    assert hasattr(i2c, "writeto") and hasattr(i2c, "readfrom_into")


def test_spi_configure_reaches_the_bus():
    # configure() used to record baudrate and reprogram nothing.
    spi = SPI(None)
    spi.configure(baudrate=2_000_000, polarity=1, phase=1)
    assert (spi._bus.baudrate, spi._bus.polarity, spi._bus.phase) == (2_000_000, 1, 1)


def test_spi_frequency_is_what_the_dividers_produce():
    # The dividers are powers of two, so asking for 3 MHz on a 16 MHz part gets 2 MHz, and
    # reporting 3 MHz back would be a number the pin never carried.
    spi = SPI(None)
    spi.configure(baudrate=3_000_000)
    assert spi.frequency == 2_000_000


def test_spi_frame_size_other_than_eight_is_refused():
    with pytest.raises(CompileError):
        SPI(None).configure(baudrate=1_000_000, bits=16)


def test_spi_buffers():
    spi = SPI(None)
    spi.write(b"\x9f")
    rx = bytearray(2)
    spi.readinto(rx)
    out = bytearray(b"\x01\x02")
    spi.write_readinto(out, rx)


def test_write_readinto_refuses_buffers_of_different_lengths():
    # It used to index in_buffer with out_buffer's index and check nothing, so a shorter
    # read buffer was written past its end.
    spi = SPI(None)
    with pytest.raises(CompileError):
        spi.write_readinto(bytearray(4), bytearray(2))

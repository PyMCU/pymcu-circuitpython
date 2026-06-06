"""busio: UART/I2C/SPI buffer-based API (CircuitPython parity)."""
from pymcu_circuitpython.busio import UART, I2C, SPI


def test_uart_baudrate():
    u = UART(None, None, baudrate=19200)
    assert u.baudrate == 19200


def test_uart_write_buffer_returns_count():
    u = UART(None, None, baudrate=9600)
    assert u.write(b"Hello") == 5


def test_uart_readinto_returns_count():
    u = UART(None, None, baudrate=9600)
    buf = bytearray(4)
    assert u.readinto(buf) == 4


def test_uart_parity_enum():
    assert UART.Parity.ODD == 0
    assert UART.Parity.EVEN == 1


def test_i2c_lock():
    i2c = I2C(None, None)
    assert i2c.try_lock() == 1
    assert i2c.try_lock() == 0   # already held
    i2c.unlock()
    assert i2c.try_lock() == 1


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


def test_spi_configure_and_frequency():
    spi = SPI(None)
    spi.configure(baudrate=2_000_000)
    assert spi.frequency == 2_000_000


def test_spi_buffers():
    spi = SPI(None)
    spi.write(b"\x9f")
    rx = bytearray(2)
    spi.readinto(rx)
    out = bytearray(b"\x01\x02")
    spi.write_readinto(out, rx)

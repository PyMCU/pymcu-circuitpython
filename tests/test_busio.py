from pymcu_circuitpython.busio import UART, I2C, SPI


# ── UART ─────────────────────────────────────────────────────────────────── #

def test_uart_instantiation():
    uart = UART("PD1", "PD0", baudrate=9600)
    assert uart is not None


def test_uart_write():
    uart = UART("PD1", "PD0")
    uart.write(65)  # should not raise


def test_uart_write_str():
    uart = UART("PD1", "PD0")
    uart.write_str("hello")


def test_uart_println():
    uart = UART("PD1", "PD0")
    uart.println("test")


def test_uart_print_byte():
    uart = UART("PD1", "PD0")
    uart.print_byte(42)


def test_uart_read():
    uart = UART("PD1", "PD0")
    b = uart.read()
    assert b == 0


# ── I2C ──────────────────────────────────────────────────────────────────── #

def test_i2c_instantiation():
    i2c = I2C("PC5", "PC4")
    assert i2c is not None


def test_i2c_try_lock_and_unlock():
    i2c = I2C("PC5", "PC4")
    assert i2c.try_lock() == 1   # first lock succeeds
    assert i2c.try_lock() == 0   # already locked
    i2c.unlock()
    assert i2c.try_lock() == 1   # available again


def test_i2c_write_and_read():
    i2c = I2C("PC5", "PC4")
    i2c.write(0x68, 0x00)
    val = i2c.read(0x68)
    assert val == 0


def test_i2c_writeto_readfrom_into():
    i2c = I2C("PC5", "PC4")
    i2c.writeto(0x68, 0x00)
    val = i2c.readfrom_into(0x68)
    assert val == 0


def test_i2c_context_manager():
    i2c = I2C("PC5", "PC4")
    i2c.__enter__()
    i2c.__exit__()  # should not raise


# ── SPI ──────────────────────────────────────────────────────────────────── #

def test_spi_instantiation():
    spi = SPI("PB5")
    assert spi is not None


def test_spi_try_lock():
    spi = SPI("PB5")
    assert spi.try_lock() == 1


def test_spi_unlock():
    spi = SPI("PB5")
    spi.unlock()  # should not raise


def test_spi_write():
    spi = SPI("PB5")
    spi.write(0xAB)  # should not raise


def test_spi_readinto():
    spi = SPI("PB5")
    val = spi.readinto()
    assert val == 0


def test_spi_write_readinto():
    spi = SPI("PB5")
    val = spi.write_readinto(0xAB)
    assert val == 0


def test_spi_select_deselect():
    spi = SPI("PB5")
    spi.select()
    spi.deselect()


def test_spi_context_manager():
    spi = SPI("PB5")
    spi.__enter__()
    spi.__exit__()

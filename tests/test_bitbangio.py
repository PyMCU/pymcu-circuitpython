"""bitbangio: the same buses as busio, driven in software on any pins (#10).

The module was absent, and the soft I2C and SPI it wraps had been in the HAL all along. It
is what a board with two sensors at the same address needs: an ATmega has one TWI.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.bitbangio import I2C, SPI


def test_the_bus_idles_with_both_lines_released():
    i2c = I2C("PD2", "PD3")
    assert i2c._bus.log == ["idle"]


def test_a_write_is_framed_and_carries_the_address_and_the_payload():
    i2c = I2C("PD2", "PD3")
    i2c._bus.log.clear()
    i2c.writeto(0x68, b"\xA5")
    assert i2c._bus.log == ["S", 0xD0, 0xA5, "P"], "0x68 shifted left with the write bit clear"


def test_a_read_acks_every_byte_but_the_last():
    i2c = I2C("PD2", "PD3")
    i2c._bus.log.clear()
    i2c.readfrom_into(0x68, bytearray(3))
    assert i2c._bus.log == ["S", 0xD1, "RA", "RA", "RN", "P"]


def test_a_repeated_start_separates_the_write_from_the_read():
    i2c = I2C("PD2", "PD3")
    i2c._bus.log.clear()
    i2c.writeto_then_readfrom(0x68, b"\x3B", bytearray(2))
    assert i2c._bus.log == ["S", 0xD0, 0x3B, "S", 0xD1, "RA", "RN", "P"]


def test_the_frequency_reaches_the_bus_as_a_half_period():
    # The half-period is a whole number of microseconds: 100 kHz is 5 us, 400 kHz is 1.
    assert I2C("PD2", "PD3", frequency=100000)._bus.half_us == 5
    assert I2C("PD2", "PD3", frequency=400000)._bus.half_us == 1


def test_the_frequency_reports_what_a_whole_microsecond_can_express():
    assert I2C("PD2", "PD3", frequency=100000).frequency == 100000
    # 300 kHz asks for a half-period of 1 us, which is 500 kHz.
    assert I2C("PD2", "PD3", frequency=300000).frequency == 500000


def test_a_frequency_the_half_period_cannot_express_is_refused():
    with pytest.raises(CompileError):
        I2C("PD2", "PD3", frequency=2000000)
    with pytest.raises(CompileError):
        I2C("PD2", "PD3", frequency=0)


def test_scan_says_what_to_use_instead():
    with pytest.raises(CompileError) as e:
        I2C("PD2", "PD3").scan()
    assert "probe" in str(e.value)


def test_the_soft_spi_clocks_the_bytes_out():
    spi = SPI("PD5", MOSI="PD6", MISO="PD7")
    spi.write(b"\x9F\x01")
    assert spi._bus.mosi_log == [0x9F, 0x01]


def test_configure_changes_the_bit_rate():
    spi = SPI("PD5", MOSI="PD6", MISO="PD7")
    spi.configure(baudrate=250000)
    assert spi._bus.half_us == 2
    assert spi.frequency == 250000


def test_a_mode_other_than_zero_is_refused_and_names_the_hardware_bus():
    spi = SPI("PD5", MOSI="PD6", MISO="PD7")
    with pytest.raises(CompileError) as e:
        spi.configure(baudrate=250000, polarity=1, phase=1)
    assert "busio.SPI" in str(e.value)


def test_a_frame_other_than_eight_bits_is_refused():
    with pytest.raises(CompileError):
        SPI("PD5", MOSI="PD6", MISO="PD7").configure(baudrate=250000, bits=16)


def test_write_readinto_refuses_buffers_of_different_lengths():
    with pytest.raises(CompileError):
        SPI("PD5", MOSI="PD6", MISO="PD7").write_readinto(bytearray(4), bytearray(2))

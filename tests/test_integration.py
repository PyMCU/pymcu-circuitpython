"""
Integration tests for pymcu_circuitpython.

These tests exercise cross-module workflows: board pin constants flowing into
peripheral constructors, typical CircuitPython usage patterns (blink, ADC→PWM,
NeoPixel), and the alarm/supervisor/microcontroller facade modules.
"""
import pytest

# ── Board imports ─────────────────────────────────────────────────────────── #

from pymcu_circuitpython.boards import arduino_uno, arduino_nano, arduino_mega, arduino_micro
from pymcu_circuitpython.boards import digispark
from pymcu_circuitpython.boards import attiny85, attiny84, attiny2313, attiny13
from pymcu_circuitpython.board_chips import BOARD_CHIPS

# ── Peripheral imports ────────────────────────────────────────────────────── #

from pymcu_circuitpython.digitalio import DigitalInOut, Direction, Pull, DriveMode
from pymcu_circuitpython.pwmio import PWMOut
from pymcu_circuitpython.analogio import AnalogIn
from pymcu_circuitpython.busio import UART, I2C, SPI
from pymcu_circuitpython.neopixel import NeoPixel
from pymcu_circuitpython import supervisor, microcontroller
from pymcu_circuitpython.alarm import time as alarm_time, pin as alarm_pin


# ── board → digitalio ─────────────────────────────────────────────────────── #

class TestBoardToDigitalIO:
    def test_uno_led_pin(self):
        led = DigitalInOut(arduino_uno.LED)
        assert led is not None

    def test_uno_led_builtin_same_as_led(self):
        assert arduino_uno.LED == arduino_uno.LED_BUILTIN

    def test_uno_d13_equals_led(self):
        assert arduino_uno.D13 == arduino_uno.LED

    def test_uno_digital_output_workflow(self):
        led = DigitalInOut(arduino_uno.D13)
        led.direction = Direction.OUTPUT
        led.value = 1
        assert led.direction == Direction.OUTPUT
        led.value = 0

    def test_uno_digital_input_with_pullup(self):
        btn = DigitalInOut(arduino_uno.D2)
        btn.direction = Direction.INPUT
        btn.pull = Pull.UP
        assert btn.pull == Pull.UP

    def test_nano_led_pin(self):
        led = DigitalInOut(arduino_nano.LED)
        assert led is not None

    def test_mega_d13_output(self):
        led = DigitalInOut(arduino_mega.D13)
        led.direction = Direction.OUTPUT
        assert led.direction == Direction.OUTPUT

    def test_micro_led_pin(self):
        led = DigitalInOut(arduino_micro.LED)
        assert led is not None

    def test_attiny85_pb1_led(self):
        led = DigitalInOut(digispark.LED)
        led.direction = Direction.OUTPUT
        assert led.direction == Direction.OUTPUT

    def test_attiny84_d0_pin(self):
        pin = DigitalInOut(attiny84.D0)
        assert pin is not None

    def test_attiny2313_d0_pin(self):
        pin = DigitalInOut(attiny2313.D0)
        assert pin is not None

    def test_attiny13_pb0_pin(self):
        pin = DigitalInOut(attiny13.PB0)
        assert pin is not None


# ── board → pwmio ─────────────────────────────────────────────────────────── #

class TestBoardToPWMOut:
    def test_uno_d6_pwm(self):
        pwm = PWMOut(arduino_uno.D6, duty_cycle=0)
        assert pwm is not None

    def test_uno_d6_duty_cycle_roundtrip(self):
        pwm = PWMOut(arduino_uno.D6, duty_cycle=32768)
        assert pwm.duty_cycle == 32768

    def test_nano_d9_pwm(self):
        pwm = PWMOut(arduino_nano.D9)
        pwm.duty_cycle = 49152
        assert pwm.duty_cycle == 49152

    def test_mega_d6_pwm(self):
        pwm = PWMOut(arduino_mega.D6)
        assert pwm is not None

    def test_digispark_pb1_pwm(self):
        # Digispark P1 is PB1, a valid PWM pin on ATtiny85
        pwm = PWMOut(digispark.P1)
        assert pwm is not None


# ── board → analogio ──────────────────────────────────────────────────────── #

class TestBoardToAnalogIn:
    def test_uno_a0_analog_in(self):
        adc = AnalogIn(arduino_uno.A0)
        assert adc is not None

    def test_uno_a5_analog_in(self):
        adc = AnalogIn(arduino_uno.A5)
        v = adc.value
        assert 0 <= v <= 65535

    def test_nano_a6_analog_in(self):
        # Nano-specific ADC-only pin
        adc = AnalogIn(arduino_nano.A6)
        assert adc is not None

    def test_nano_a7_analog_in(self):
        adc = AnalogIn(arduino_nano.A7)
        v = adc.read_u16()
        assert isinstance(v, int)

    def test_mega_a0_analog_in(self):
        adc = AnalogIn(arduino_mega.A0)
        assert adc is not None

    def test_attiny85_a1(self):
        adc = AnalogIn(attiny85.A1)
        assert adc is not None


# ── board → busio ─────────────────────────────────────────────────────────── #

class TestBoardToBusIO:
    # UART
    def test_uno_uart_via_board_pins(self):
        uart = UART(arduino_uno.TX, arduino_uno.RX, baudrate=9600)
        assert uart is not None

    def test_uno_uart_write_str(self):
        uart = UART(arduino_uno.TX, arduino_uno.RX)
        uart.write_str("hello")  # must not raise

    def test_nano_uart(self):
        uart = UART(arduino_nano.TX, arduino_nano.RX, baudrate=115200)
        uart.println("test")

    def test_mega_uart(self):
        uart = UART(arduino_mega.TX, arduino_mega.RX)
        assert uart is not None

    # I2C
    def test_uno_i2c_via_board_pins(self):
        i2c = I2C(arduino_uno.SCL, arduino_uno.SDA)
        assert i2c is not None

    def test_uno_i2c_lock_cycle(self):
        i2c = I2C(arduino_uno.SCL, arduino_uno.SDA)
        assert i2c.try_lock() == 1
        i2c.unlock()
        assert i2c.try_lock() == 1

    def test_uno_i2c_context_manager(self):
        i2c = I2C(arduino_uno.SCL, arduino_uno.SDA)
        i2c.__enter__()
        i2c.__exit__()

    def test_mega_i2c(self):
        i2c = I2C(arduino_mega.SCL, arduino_mega.SDA)
        assert i2c is not None

    # SPI
    def test_uno_spi_via_board_pins(self):
        spi = SPI(arduino_uno.SCK, MOSI=arduino_uno.MOSI, MISO=arduino_uno.MISO)
        assert spi is not None

    def test_uno_spi_write_readinto(self):
        spi = SPI(arduino_uno.SCK)
        result = spi.write_readinto(0xAB)
        assert isinstance(result, int)

    def test_uno_spi_context_manager(self):
        spi = SPI(arduino_uno.SCK)
        spi.__enter__()
        spi.__exit__()


# ── NeoPixel ──────────────────────────────────────────────────────────────── #

class TestNeoPixel:
    def test_instantiation_with_board_pin(self):
        px = NeoPixel(arduino_uno.D6, 8)
        assert px is not None

    def test_n_stored(self):
        px = NeoPixel(arduino_uno.D6, 4)
        assert px._n == 4

    def test_fill_does_not_raise(self):
        px = NeoPixel(arduino_uno.D6, 8)
        px.fill(255, 0, 0)

    def test_set_pixel_does_not_raise(self):
        px = NeoPixel(arduino_uno.D6, 8)
        px.set_pixel(0, 0, 255, 0)

    def test_show_does_not_raise(self):
        px = NeoPixel(arduino_uno.D6, 8)
        px.show()

    def test_deinit_does_not_raise(self):
        px = NeoPixel(arduino_uno.D6, 8)
        px.deinit()

    def test_digispark_pin(self):
        px = NeoPixel(digispark.P0, 1)
        px.fill(0, 0, 255)
        px.show()


# ── supervisor ────────────────────────────────────────────────────────────── #

class TestSupervisor:
    def test_ticks_ms_returns_int(self):
        t = supervisor.ticks_ms()
        assert isinstance(t, int)

    def test_ticks_ms_is_zero(self):
        # Stub always returns 0
        assert supervisor.ticks_ms() == 0

    def test_runtime_is_none(self):
        assert supervisor.runtime is None


# ── microcontroller ───────────────────────────────────────────────────────── #

class TestMicrocontroller:
    def test_cpu_frequency(self):
        freq = microcontroller.cpu.frequency
        assert freq == 16_000_000

    def test_cpu_temperature_raises(self):
        with pytest.raises(NotImplementedError):
            _ = microcontroller.cpu.temperature

    def test_cpu_reset_raises(self):
        with pytest.raises(NotImplementedError):
            microcontroller.cpu.reset()


# ── alarm ─────────────────────────────────────────────────────────────────── #

class TestAlarm:
    def test_time_alarm_creation(self):
        ta = alarm_time.TimeAlarm(monotonic_time=500)
        assert ta._ms == 500

    def test_time_alarm_zero(self):
        ta = alarm_time.TimeAlarm(monotonic_time=0)
        assert ta._ms == 0

    def test_pin_alarm_creation(self):
        pa = alarm_pin.PinAlarm(arduino_uno.D2, value=1)
        assert pa._pin_name == arduino_uno.D2
        assert pa._value == 1

    def test_pin_alarm_low_value(self):
        pa = alarm_pin.PinAlarm(arduino_uno.D2, value=0)
        assert pa._value == 0


# ── board_chips ───────────────────────────────────────────────────────────── #

class TestBoardChips:
    def test_digispark_maps_to_attiny85(self):
        assert BOARD_CHIPS["digispark"] == "attiny85"

    def test_adafruit_trinket_maps_to_attiny85(self):
        assert BOARD_CHIPS["adafruit_trinket"] == "attiny85"

    def test_attiny85_family(self):
        assert BOARD_CHIPS["attiny85"] == "attiny85"
        assert BOARD_CHIPS["attiny45"] == "attiny45"
        assert BOARD_CHIPS["attiny25"] == "attiny25"

    def test_attiny84_family(self):
        assert BOARD_CHIPS["attiny84"] == "attiny84"
        assert BOARD_CHIPS["attiny44"] == "attiny44"
        assert BOARD_CHIPS["attiny24"] == "attiny24"

    def test_attiny2313_family(self):
        assert BOARD_CHIPS["attiny2313"] == "attiny2313"
        assert BOARD_CHIPS["attiny4313"] == "attiny4313"

    def test_attiny13_family(self):
        assert BOARD_CHIPS["attiny13"] == "attiny13"
        assert BOARD_CHIPS["attiny13a"] == "attiny13a"

    def test_all_values_are_strings(self):
        for board_name, chip in BOARD_CHIPS.items():
            assert isinstance(chip, str), f"{board_name!r} chip must be a string"

    def test_all_keys_are_strings(self):
        for board_name in BOARD_CHIPS:
            assert isinstance(board_name, str)


# ── typical workflows ─────────────────────────────────────────────────────── #

class TestTypicalWorkflows:
    def test_blink_pattern(self):
        """Simulate a blink sketch: set up LED output, toggle 3 times."""
        led = DigitalInOut(arduino_uno.LED)
        led.direction = Direction.OUTPUT
        for _ in range(3):
            led.value = 1
            led.value = 0

    def test_button_led_pattern(self):
        """Input pin with pull-up controlling output LED."""
        btn = DigitalInOut(arduino_uno.D2)
        btn.direction = Direction.INPUT
        btn.pull = Pull.UP

        led = DigitalInOut(arduino_uno.D13)
        led.direction = Direction.OUTPUT

        # Simulate: if button low, turn on LED
        if btn.value == 0:
            led.value = 1
        else:
            led.value = 0

    def test_adc_to_pwm_pattern(self):
        """Read ADC value and map to PWM duty cycle."""
        adc = AnalogIn(arduino_uno.A0)
        pwm = PWMOut(arduino_uno.D6)

        raw = adc.value           # 16-bit (0-65535)
        pwm.duty_cycle = raw      # directly assign

        assert pwm.duty_cycle == raw

    def test_uart_echo_pattern(self):
        """Read a byte and echo it back."""
        uart = UART(arduino_uno.TX, arduino_uno.RX, baudrate=9600)
        b = uart.read()
        uart.write(b)

    def test_i2c_sensor_read_pattern(self):
        """Write register address then read sensor data."""
        i2c = I2C(arduino_uno.SCL, arduino_uno.SDA)
        i2c.__enter__()
        i2c.write(0x68, 0x3B)   # write register address
        val = i2c.read(0x68)     # read result
        i2c.__exit__()
        assert isinstance(val, int)

    def test_spi_transfer_pattern(self):
        """Full-duplex SPI transfer with chip-select."""
        spi = SPI(arduino_uno.SCK, MOSI=arduino_uno.MOSI, MISO=arduino_uno.MISO)
        spi.__enter__()
        result = spi.write_readinto(0xAB)
        spi.__exit__()
        assert isinstance(result, int)

    def test_neopixel_rainbow_fill(self):
        """Fill strip with three different colours sequentially."""
        px = NeoPixel(arduino_uno.D6, 8)
        for r, g, b in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            px.fill(r, g, b)
            px.show()

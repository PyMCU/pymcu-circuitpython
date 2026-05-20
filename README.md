# pymcu-circuitpython

CircuitPython compatibility layer for PyMCU. Write CircuitPython code and compile it to bare-metal microcontroller firmware.

## Installation

```bash
pip install pymcu-circuitpython
```

Or add to your `pyproject.toml`:

```toml
[project]
dependencies = ["pymcu", "pymcu-circuitpython"]

[tool.pymcu]
stdlib = ["circuitpython"]
board = "arduino_uno"      # Auto-generates board.py with pin definitions
frequency = 16000000
```

**Important:** Use `board = "arduino_uno"` instead of `chip = "atmega328p"` to enable auto-generation of the `board` module with CircuitPython-style pin names (LED, D13, A0, etc.). The build driver will:
1. Detect the board name from `pyproject.toml`
2. Copy the appropriate board file from `pymcu_circuitpython/boards/<board>.py`
3. Generate `dist/_generated/board.py` so `import board` works seamlessly

## Supported Modules

### Core Modules

| Module | Classes/Functions | Status | Notes |
|--------|------------------|--------|-------|
| `board` | Pin constants (D0-D13, A0-A5, LED, TX, RX, etc.) | ✅ Complete | Arduino Uno pin mapping |
| `digitalio` | `DigitalInOut`, `Direction`, `Pull`, `DriveMode` | ✅ Complete | ZCA properties for `.direction`, `.value`, `.pull`, `.drive_mode` |
| `analogio` | `AnalogIn`, `AnalogOut` | ✅ Complete | 16-bit ADC values (scaled from 10-bit), AnalogOut raises error (no DAC) |
| `busio` | `UART`, `SPI`, `I2C` | ⚠️ Partial | UART complete, SPI/I2C TODO |
| `pwmio` | `PWMOut` | ✅ Complete | 16-bit duty cycle (scaled to 8-bit Timer0/Timer2) |
| `time` | `sleep()`, `sleep_ms()`, `sleep_us()` | ✅ Complete | Integer seconds (no float) |
| `microcontroller` | `cpu.frequency`, `Pin` | ⚠️ Partial | Compile-time constants only |

### Feature Comparison

| Feature | CircuitPython | pymcu-circuitpython |
|---------|---------------|---------------------|
| `led.direction = Direction.OUTPUT` | ✅ | ✅ |
| `led.value = True` | ✅ | ✅ |
| `adc.value` (16-bit) | ✅ | ✅ |
| `pwm.duty_cycle = 32768` | ✅ | ✅ |
| `uart.write(b"hello")` | ✅ | ⚠️ `uart.write_str("hello")` |
| `time.sleep(0.5)` | ✅ | ⚠️ `time.sleep_ms(500)` |
| `time.sleep_ms(100)` | ✅ | ✅ |
| `import board` | ✅ | ✅ |
| `board.LED` | ✅ | ✅ |

## Quick Start

### Blink Example

```python
import board
from digitalio import DigitalInOut, Direction
from time import sleep_ms


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    while True:
        led.value = True
        sleep_ms(500)
        led.value = False
        sleep_ms(500)
```

### ADC + PWM Example

```python
import board
from analogio import AnalogIn
from pwmio import PWMOut
from time import sleep_ms


def main():
    pot = AnalogIn(board.A0)
    led = PWMOut(board.D6, duty_cycle=0)

    while True:
        led.duty_cycle = pot.value  # 0-65535
        sleep_ms(10)
```

### UART Example

```python
import board
import busio
from digitalio import DigitalInOut, Direction


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    uart = busio.UART(board.TX, board.RX, baudrate=9600)
    uart.println("READY")

    while True:
        byte = uart.read()
        led.value = 1
        uart.write(byte)
        led.value = 0
```

## Differences from Real CircuitPython

### Type Annotations Required

PyMCU requires explicit type annotations for all variables:

```python
# CircuitPython
count = 0

# pymcu-circuitpython
from pymcu.types import uint8
count: uint8 = 0
```

### No Float Support (Yet)

Use integer arithmetic with fixed-point scaling:

```python
# CircuitPython
temp_c = raw * 3.3 / 1024 * 100

# pymcu-circuitpython
from pymcu.types import uint16
temp_c: uint16 = raw * 330 // 1024  # Multiply first, divide last
```

### No Runtime Exceptions

Replace `try/except` with error codes and `match/case`:

```python
# CircuitPython
try:
    val = sensor.read()
except RuntimeError:
    val = 0

# pymcu-circuitpython
val: uint16 = sensor.read()  # Returns 0xFFFF on error
if val == 0xFFFF:
    val = 0
```

### No F-Strings (Yet)

Use UART write methods:

```python
# CircuitPython
print(f"temp={temp}")

# pymcu-circuitpython
uart.write_str("temp=")
uart.print_byte(temp)
```

### Sleep Uses Integers

Use milliseconds instead of float seconds:

```python
# CircuitPython
time.sleep(0.5)

# pymcu-circuitpython
time.sleep_ms(500)
```

## Supported Boards

**⚠️ AVR-Only Support:** CircuitPython compatibility is currently **AVR-only**. PyMCU's only fully working codegen is for AVR chips (ATmega328P and compatible).

The `board` module is auto-generated based on the `board` setting in `pyproject.toml`:

| Board Name | Chip | Status | Notes |
|------------|------|--------|-------|
| `arduino_uno` | ATmega328P | ✅ Complete | Full support with all modules |
| `arduino_nano` | ATmega328P | ✅ Complete | Same pins as Uno |

**Future AVR Boards (needs validation):**
- `arduino_mega` (ATmega2560) - AVR Mega codegen needs testing
- `arduino_micro` (ATmega32U4) - AVR Mega codegen needs testing

**Other Architectures (not yet supported):**
- SAMD21/SAMD51 (Feather M0/M4) - Requires SAMD backend
- RP2040 (Raspberry Pi Pico) - Requires full RP2040 CPU support
- PIC14/PIC18 - Requires PIC backend improvements for CircuitPython stdlib

**Adding Custom AVR Boards:**
1. Create `pymcu_circuitpython/boards/<your_board>.py` with pin definitions
2. If needed, add to `board_chips.py`: `BOARD_CHIPS["your_board"] = "atmega328p"`
3. Set `board = "your_board"` in `pyproject.toml`

**Important:** Only create board files for chips with **fully working codegen**. Do not create placeholders.

## Examples

See `examples/` directory for complete projects:

- `blink/` - Basic LED blink
- `button-led/` - Button input with LED output
- `uart-echo/` - Serial echo with LED indicator
- `adc-pwm/` - Potentiometer-controlled PWM dimming
- `morse-blinker/` - Morse code SOS pattern
- `traffic-light/` - Traffic light state machine
- `dht-sensor/` - DHT11 temperature/humidity sensor

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR at:
- PyMCU compiler: https://github.com/pymcu/pymcu
- CircuitPython compat: https://github.com/pymcu/pymcu-circuitpython

## See Also

- [PyMCU Documentation](https://pymcu.dev)
- [CircuitPython](https://circuitpython.org)
- [Language Reference](https://pymcu.dev/language-reference)

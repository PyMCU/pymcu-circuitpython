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
| `digitalio` | `DigitalInOut`, `Direction`, `Pull`, `DriveMode` | ✅ Complete | ZCA properties `.direction`, `.value`, `.pull`, `.drive_mode`; `pull=None` and `Pull.UP` (AVR has no pull-down) |
| `analogio` | `AnalogIn`, `AnalogOut` | ✅ Complete | Full-scale `value` (1023 counts map to 65535); `reference_voltage` comes from the HAL; a pin with no channel and `AnalogOut` are refused where written |
| `busio` | `UART`, `SPI`, `I2C` | ✅ Complete | Every parameter reaches the hardware: frame format, bit rates, SPI mode, `timeout`. `in_waiting` is a count; `read()`/`readline()`/`scan()` are refused, naming `readinto`/`probe` |
| `bitbangio` | `I2C`, `SPI` | ✅ Complete | The same API as `busio`, on any pins. Mode 0 only for SPI |
| `pwmio` | `PWMOut` | ✅ Complete | 16-bit duty cycle; `frequency` reports what the pin emits. On D9/D10 the frequency is exact, which is what makes a servo work |
| `pulseio` | `PulseIn`, `PulseOut` | ✅ ATmega 48/88/168/328 | Pulse lengths in microseconds; a 38 kHz carrier gated by a pulse list. `send(pulses, count)` takes the count |
| `countio` | `Counter`, `Edge` | ✅ Complete | A pin interrupt and a 32-bit count. One per program; a single edge needs D2 or D3 |
| `keypad` | `Keys`, `Event` | ⚠️ Partial | Takes a list of `DigitalInOut`, not pin names. `KeyMatrix` is not written |
| `rainbowio` | `colorwheel` | ✅ Complete | Red, green, blue and back across 0 to 255 |
| `adafruit_motor.servo` | `Servo`, `ContinuousServo` | ✅ On D9/D10 | Import it as `from adafruit_motor.servo import Servo` |
| `time` | `sleep()`, `monotonic()`, `monotonic_ns()` | ✅ Complete | `sleep()` takes any duration, from microseconds to minutes; `monotonic_ns()` wraps at 4.295 s and says so |
| `supervisor` | `ticks_ms/add/diff`, `reload`, `runtime` | ✅ Complete | 2²⁹ ms wrap and signed `ticks_diff`, matching CircuitPython |
| `microcontroller` | `cpu.*`, `nvm`, `watchdog`, `reset()`, `delay_us()` | ✅ Complete | `len(nvm)` is the part's EEPROM; `watchdog.mode = None` disables it; `uid` is refused rather than eight zeros |
| `neopixel` | `NeoPixel` | ✅ Yes | Ships in [pymcu-lib-neopixel](https://github.com/PyMCU/pymcu-lib-neopixel), pulled in as a dependency: `import neopixel` is unchanged |
| `neopixel_write` | `neopixel_write` | ✅ ATmega 48/88/168/328 | The low-level one-wire write the guides call directly. Takes a `DigitalInOut` and a buffer, and does not reorder it: a WS2812 wants green, red, blue. Mask interrupts around it if a timer is running |
| `alarm` | `TimeAlarm`, `PinAlarm`, `sleep_until_alarms` | ✅ Complete | Up to four alarms at once; the return value is which one fired, because an alarm object cannot come back |

### Feature Comparison

| Feature | CircuitPython | pymcu-circuitpython |
|---------|---------------|---------------------|
| `led.direction = Direction.OUTPUT` | ✅ | ✅ |
| `led.value = True` | ✅ | ✅ |
| `adc.value` (16-bit) | ✅ | ✅ |
| `pwm.duty_cycle = 32768` | ✅ | ✅ |
| `uart.write(b"hello")` | ✅ | ✅ |
| `uart.readinto(buf)` | ✅ | ✅ (buf is a `uint8[N]`) |
| `time.sleep(0.5)` | ✅ | ✅ |
| `supervisor.ticks_diff(a, b)` | ✅ | ✅ |
| `microcontroller.reset()` | ✅ | ✅ (watchdog) |
| `import board` | ✅ | ✅ |
| `board.LED` | ✅ | ✅ |

### Known limitations (not implementable on bare-metal AVR)

Each of these is **refused where it is written**, with a message naming what does work,
rather than compiling to something that does nothing.

- `uart.read()`, `uart.readline()`, `i2c.scan()` and `keypad`'s `events.get()` return heap
  objects (`bytes`, `list`, an `Event`). Use `uart.readinto(buf)`, `i2c.probe(addr)` in a
  loop, and `events.get_into(event)`.
- `analogio.AnalogOut` needs a digital-to-analog converter and no AVR part has one; the
  refusal names `pwmio.PWMOut` with an RC filter.
- `microcontroller.cpu.uid`: this part has no unique serial anyone documents. Write a random
  value into `microcontroller.nvm` at first boot and read it back.
- `pulseio.PulseOut.send(pulses, count)` takes the count, because a module-level array loses
  its length when it crosses a parameter.
- `keypad.Keys` takes a list of `digitalio.DigitalInOut`, not a list of pin names.
- `rotaryio` and `keypad.KeyMatrix` are not implemented yet.
- `neopixel` (from `pymcu-lib-neopixel`): whole-strip `fill((r, g, b))` and addressable
  `pixels[i] = (r, g, b)` both work, backed by a per-strip SRAM framebuffer
  (3 bytes/pixel). The packed `fill(0xRRGGBB)` integer form is not
  simultaneously dispatchable with the tuple form, so the tuple form is the
  supported one.
- Receive buffers are fixed-size `uint8[N]` arrays rather than `bytearray(N)`.

### Not implemented (no hardware to back them, on this class of chip)

These symbols simply do not exist in the layer, rather than being refused at the point
they are written: there is no AVR peripheral or runtime concept underneath them.

- `wifi.*` and `socketpool.*`: none of the AVR parts this layer targets has a WiFi radio,
  so there is no radio, network interface, or socket layer to back `wifi.Radio`,
  `wifi.Network`, `wifi.Monitor`, `wifi.AuthMode`, `wifi.Packet`, `wifi.PowerManagement`,
  `wifi.ScannedNetworks`, `socketpool.SocketPool` or `socketpool.Socket`.
- `supervisor.get_setting` reads `/settings.toml`, `supervisor.reset_terminal` resizes the
  REPL's serial terminal, and `supervisor.set_next_code_file` chooses which file a dynamic
  boot search runs next: none of that exists here, because a PyMCU build is one fixed
  program compiled ahead of time onto one fixed file, with no filesystem, no REPL and no
  boot-time file search.
- `supervisor.Runtime`, `supervisor.StatusBar`, `supervisor.status_bar`,
  `supervisor.set_usb_identification` and `supervisor.RunReason`/`supervisor.SafeModeReason`
  describe USB enumeration, an on-display status bar, and why CircuitPython's own supervisor
  started or fell back to safe mode; a bare-metal AVR build has no USB stack, no display, no
  auto-reload, and no safe-mode fallback runtime to report on.
- `supervisor.get_previous_traceback` reads back the previous run's exception text; PyMCU's
  exception model carries no message string across a crash for anything to return here.
- `alarm.SleepMemory`/`alarm.sleep_memory` persist state across a real deep sleep that powers
  the chip down and restarts the interpreter. This part's alarm functions do not do that
  (see the `alarm` row above: they block in place rather than actually sleeping), so there
  is no separate always-on RAM region to back a `SleepMemory`.
- `keypad.ShiftRegisterKeys` is not implemented either: it reads a key matrix through a
  shift-register chip, a different peripheral than the pin-per-key `keypad.Keys` this layer
  has.
- `watchdog.WatchDogTimeout`, the exception `WatchDogMode.RAISE` expiry raises, is not
  implemented either, because `WatchDogMode.RAISE` itself is refused (see `watchdog.py`):
  this HAL only programs the watchdog's reset behaviour, not the interrupt-and-continue
  behaviour `RAISE` needs.

### API parity testing

`tests/parity/` checks this layer's public API against the official `circuitpython-stubs`
package. That package does not ship separate `sys-stubs`/`time-stubs` packages: CircuitPython
documents both modules as compatible with the equivalent CPython/typeshed modules rather than
redocumenting them, so this repository's own module docs (above) are the parity reference for
`sys` and `time` instead of a stub file.

## Quick Start

### Blink Example

```python
import board
from digitalio import DigitalInOut, Direction
from time import sleep


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    while True:
        led.value = True
        sleep(0.5)
        led.value = False
        sleep(0.5)
```

### ADC + PWM Example

```python
import board
from analogio import AnalogIn
from pwmio import PWMOut
from time import sleep


def main():
    pot = AnalogIn(board.A0)
    led = PWMOut(board.D6, duty_cycle=0)

    while True:
        led.duty_cycle = pot.value  # 0-65535, full scale on the pin reads 65535
        sleep(0.01)
```

### UART Example

```python
import board
import busio
from digitalio import DigitalInOut, Direction


def main():
    led = DigitalInOut(board.LED)
    led.direction = Direction.OUTPUT

    uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=500)
    uart.write(b"READY\r\n")

    buf = bytearray(1)
    while True:
        if uart.readinto(buf):
            led.value = True
            uart.write(buf)
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

Use `print()`, which takes an f-string and streams it:

```python
print(f"temp={temp}")
```

### Sleep takes float seconds, as upstream

```python
time.sleep(0.5)        # half a second
time.sleep(0.0005)     # 500 microseconds
time.sleep(120)        # two minutes
```

It used to go through a 16-bit millisecond count, so anything past 65.535 seconds wrapped
and anything under a millisecond did not sleep at all. `sleep_ms()` and `sleep_us()` also
exist, but they are **PyMCU extensions**: upstream `time` defines no such names, so code
using them will not run under real CircuitPython.

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
- `neopixel/` - Addressable WS2812 strip (`fill`, `pixels[i] = (r, g, b)`, `show`)

## Testing

`tests/parity/` checks this layer's real API surface against `circuitpython-stubs`, symbol by
symbol, and runs on every push and PR (pure CPython, no compiler needed). `tests/corpus/`
builds 49 user-style programs with the pinned `pymcu-compiler[avr]` release from PyPI and
enforces the flash-size baseline in `tests/corpus/sizes.json`; it also runs in CI, in its own
job. Both are defined in `.github/workflows/ci.yml`.

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

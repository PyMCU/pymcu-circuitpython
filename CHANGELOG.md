# Changelog — pymcu-circuitpython

## 0.1.0b1 (frozen at 552e44c, 2026-09-15)

Beta 1: this layer moves out of alpha alongside the frontend
(`pymcu-compiler`/`pymcu-stdlib` 0.1.0b1) and the AVR backend
(`pymcu-avr` 0.1.0b1), since AVR is the only chip family with real
CircuitPython hardware to compare against. Coverage on RP2040/RP2350
tracks the ARM backend, which stays alpha; `keypad.KeyMatrix` (#13)
and the storage/os modules (#16) are out of beta 1 by decision.

### Added

- **boards**: adafruit_trinket, and pico as an alias of raspberry_pi_pico
- **microcontroller**: disable_interrupts and enable_interrupts
- a micropython module, providing const and nothing else
- a sys module, providing implementation.name and nothing else
- **boards**: board.I2C(), board.SPI() and board.UART() on the AVR Arduino boards ([#7](https://github.com/PyMCU/pymcu-circuitpython/issues/7))
- **pulseio**: PulseIn and PulseOut ([#9](https://github.com/PyMCU/pymcu-circuitpython/issues/9))
- **servo**: adafruit_motor.servo, so an angle lands on its pulse width ([#8](https://github.com/PyMCU/pymcu-circuitpython/issues/8))
- **bitbangio**: the same buses as busio, driven in software on any pins ([#10](https://github.com/PyMCU/pymcu-circuitpython/issues/10))
- **rainbowio**: colorwheel(pos), the colour at a position on the wheel ([#15](https://github.com/PyMCU/pymcu-circuitpython/issues/15))
- **countio**: Counter, the edges that arrived on a pin ([#11](https://github.com/PyMCU/pymcu-circuitpython/issues/11))
- **keypad**: Keys and Event, which button changed and which way ([#13](https://github.com/PyMCU/pymcu-circuitpython/issues/13))
- **boards**: board.I2C(), board.SPI() and board.UART() are back ([#7](https://github.com/PyMCU/pymcu-circuitpython/issues/7))
- **rotaryio**: IncrementalEncoder, where a two-track knob has turned to ([#12](https://github.com/PyMCU/pymcu-circuitpython/issues/12))
- **boards**: the bare 8-pin ATtinys answer to board.Dn
- **neopixel_write**: the low-level one-wire write, as CircuitPython spells it
- **analogio,countio,digitalio,keypad,pwmio,rotaryio**: __exit__ matches upstream's (self, *args) arity
- **busio**: start/end and configure() become keyword-only, matching upstream
- **bitbangio**: start/end/configure() become keyword-only; write()'s buffer is spelled buf, and configure()'s baudrate default matches upstream's 100000
- **pulseio**: PulseIn.__bool__ answers len(pulses) > 0; __exit__ matches upstream's arity
- **watchdog**: WatchDogTimer is exported as the type of microcontroller.watchdog
- **microcontroller**: implement RunMode and on_next_reset
- **keypad**: Event gains timestamp, EventQueue is public, __bool__ added

### Fixed

- **microcontroller**: cpu.frequency returns the clock instead of failing to compile
- remove two MicroPython spellings and move WatchDogMode where upstream keeps it
- **alarm**: the tail is written as the else it already logically is
- **net**: refuse on a chip with no radio, and say that is the reason
- **pwmio**: PWMOut.frequency reprograms the timer, and is refused without variable_frequency ([#5](https://github.com/PyMCU/pymcu-circuitpython/issues/5))
- **pwmio**: deinit() releases the pin as an input ([PyMCU#296](https://github.com/PyMCU/PyMCU/issues/296))
- **pwmio**: the constructor leaves the start to the HAL ([PyMCU#296](https://github.com/PyMCU/PyMCU/issues/296))
- **pwmio**: duty_cycle goes to the HAL as the 16-bit value it is ([#30](https://github.com/PyMCU/pymcu-circuitpython/issues/30))
- **digitalio**: deinit() releases the pin without pull, and switch_to_output sets the level first ([PyMCU#309](https://github.com/PyMCU/PyMCU/issues/309))
- **analogio**: the value covers the whole range, the reference is the chip's, and AnalogOut is refused where there is no DAC ([#21](https://github.com/PyMCU/pymcu-circuitpython/issues/21))
- **busio**: every parameter reaches the hardware or is refused, and a read has a deadline ([#22](https://github.com/PyMCU/pymcu-circuitpython/issues/22), [#23](https://github.com/PyMCU/pymcu-circuitpython/issues/23), [#24](https://github.com/PyMCU/pymcu-circuitpython/issues/24))
- **pwmio**: frequency reports what the pin emits, and the first parameter is pin ([#18](https://github.com/PyMCU/pymcu-circuitpython/issues/18))
- **time, supervisor, nvm, watchdog**: four values that were not the part's ([#26](https://github.com/PyMCU/pymcu-circuitpython/issues/26), [#25](https://github.com/PyMCU/pymcu-circuitpython/issues/25), [#16](https://github.com/PyMCU/pymcu-circuitpython/issues/16), [#19](https://github.com/PyMCU/pymcu-circuitpython/issues/19))
- **microcontroller**: uid refused rather than eight zeros, cpus has a length ([#27](https://github.com/PyMCU/pymcu-circuitpython/issues/27))
- **alarm**: wait on several alarms, and say which one fired ([#20](https://github.com/PyMCU/pymcu-circuitpython/issues/20))
- **time**: sleep() folds to one calibrated delay for a literal duration ([#26](https://github.com/PyMCU/pymcu-circuitpython/issues/26))
- **microcontroller**: len(nvm) is a literal again, because a slice of nvm needs one ([#16](https://github.com/PyMCU/pymcu-circuitpython/issues/16))
- **digitalio**: switch_to_output's value default is False, as upstream spells it
- **micropython**: const()'s parameter is named expr, as upstream spells it
- **rainbowio**: colorwheel()'s parameter is named n, as upstream spells it
- **watchdog**: move WatchDogTimer into watchdog.py, breaking the import cycle

### Changed

- **time**: sleep() written with plain locals now that a constant survives one ([PyMCU#327](https://github.com/PyMCU/PyMCU/issues/327))

### Documentation

- the README describes the modules and the spellings that exist ([#29](https://github.com/PyMCU/pymcu-circuitpython/issues/29))
- neopixel_write joins the supported module table
- **corpus**: triage the refused programs
- **readme**: document the API surface this class of AVR chip will not provide
- **parity**: regenerate the parity report

### Tests

- the conftest stubs __CHIP__ as an object, pymcu.hal.irq, __FREQ__ and the layer's own module names ([#6](https://github.com/PyMCU/pymcu-circuitpython/issues/6))
- the conftest binds __TIMEBASE__ like __FREQ__ ([PyMCU#295](https://github.com/PyMCU/PyMCU/issues/295))
- the analogio mocks follow the HAL's ADC and DAC, and the tests measure what changed ([#21](https://github.com/PyMCU/pymcu-circuitpython/issues/21))
- the busio mocks follow the HAL, and the tests measure what reaches the hardware ([#22](https://github.com/PyMCU/pymcu-circuitpython/issues/22), [#23](https://github.com/PyMCU/pymcu-circuitpython/issues/23), [#24](https://github.com/PyMCU/pymcu-circuitpython/issues/24), [#7](https://github.com/PyMCU/pymcu-circuitpython/issues/7))
- pulse mocks that behave like the HAL, and refuse like it ([#9](https://github.com/PyMCU/pymcu-circuitpython/issues/9))
- the PWM mock reports the frequency the pin emits ([#18](https://github.com/PyMCU/pymcu-circuitpython/issues/18), [#8](https://github.com/PyMCU/pymcu-circuitpython/issues/8))
- soft I2C and SPI mocks that log what they clocked out ([#10](https://github.com/PyMCU/pymcu-circuitpython/issues/10))
- an edge-counter mock that refuses a single edge where the pin cannot tell ([#11](https://github.com/PyMCU/pymcu-circuitpython/issues/11))
- the four values, and an EEPROM mock that has a size ([#26](https://github.com/PyMCU/pymcu-circuitpython/issues/26), [#25](https://github.com/PyMCU/pymcu-circuitpython/issues/25), [#16](https://github.com/PyMCU/pymcu-circuitpython/issues/16), [#19](https://github.com/PyMCU/pymcu-circuitpython/issues/19))
- the mock clock advances, because alarm waits on it ([#20](https://github.com/PyMCU/pymcu-circuitpython/issues/20))
- add a corpus of user-style programs with expected build outcomes and size gates
- add CircuitPython API parity suite
- **parity**: resolve symbolic stub defaults and accept __exit__(self, *args)
- **parity**: allowlist real gaps tracked as GitHub issues
- **corpus**: create the template's src directory, which git does not keep empty
- **corpus**: resolve the pymcu driver from PyMCU's own repo venv, not a user project
- **corpus**: flip four fixed programs to build, refresh all sizes

### CI

- add API parity and corpus GitHub Actions workflows

### Reverted

- board.I2C(), board.SPI() and board.UART(), which miscompile busio ([#7](https://github.com/PyMCU/pymcu-circuitpython/issues/7))


## 0.1.0a2 — 2026-08-18

Everything the PyPI 0.1.0a1 layer (June) predates. With the 0.1.0a10
compiler, the canonical CircuitPython nvm pattern works end-to-end:
`microcontroller.nvm[0:4] = b'...'` and `print(microcontroller.nvm[0:4])`
print the real CPython bytearray repr, verified against EEPROM on a real
Arduino Uno.

### New
- `microcontroller.nvm`: EEPROM-backed persistent byte storage.
- `microcontroller.watchdog` (WatchDogTimer) and
  `microcontroller.cpu.reset_reason` / `ResetReason`.
- RP2040 support: board/digitalio/busio dispatch by architecture.

### Changed
- NeoPixel moved to its own library (pymcu-lib-neopixel).

### Requires
- pymcu-compiler >= 0.1.0a10 for the nvm slice forms; single-byte
  `nvm[i]` access works with earlier compilers.

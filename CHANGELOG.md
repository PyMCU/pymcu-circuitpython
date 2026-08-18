# Changelog — pymcu-circuitpython

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

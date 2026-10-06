# Game of Life on an SSD1306 OLED

Conway's Game of Life on a 128x64 SSD1306 I2C OLED, through the unmodified
Adafruit CircuitPython SSD1306 / framebuf stack. A 32x16 grid of 4x4-pixel
cells evolves once every 0.1 s; a dead or frozen world holds for a second
and reseeds with a fresh random soup.

The 128x64 panel's framebuffer alone is 1025 bytes, and the Arduino Uno has
2 KB of SRAM total. The straightforward port, two full 32x16 grids
(`cells` and `next_cells`, the way the 128x32 version does it), does not
fit: the compiler refuses the build with `static data needs 2288 bytes but
atmega328p has 2048 bytes of SRAM`. `Life.step()` here uses a single grid
instead, updated row by row in place, with two rows kept as backup (the
previous row, and row 0, needed again at the last row because the board
wraps top to bottom) so each row's neighbour count still sees the right,
unmodified values. That brings the two grids worth of state down to one
grid plus two rows: measured at 1606/2048 bytes of static SRAM, 442 bytes
free before the call stack. The single-grid algorithm was checked against
the two-grid one in plain CPython, 200 generations, 0 differences, before
it replaced it here.

The random soup comes from a small linear congruential generator written in
plain Python, not the `random` module: `random` differs between CPython,
CircuitPython and PyMCU, while the LCG computes the same 31-bit sequence on
all three, which is what makes the rendered GIF in the docs gallery page
reproducible from an emulator run.

## Wiring

I2C only: SCL to A5, SDA to A4, VCC at the module's own voltage (3V3 or 5V
depending on the module -- check its datasheet). No display needs to be
present to build or flash; the program just won't show anything without one.

## Get the Adafruit drivers

This example does not vendor the Adafruit libraries; they are not PyMCU
code, and copying them here would drift out of date. Install the official
packages and copy the plain `.py` files (and the font) into `src/`:

```bash
pip install adafruit-circuitpython-ssd1306 adafruit-circuitpython-framebuf adafruit-circuitpython-busdevice
```

Then, from that environment's `site-packages`, copy into this example's
`src/` directory:

- `adafruit_ssd1306.py`
- `adafruit_framebuf.py` and `font5x8.bin`
- the `adafruit_bus_device/` package (`__init__.py`, `i2c_device.py`,
  `spi_device.py`)

This example was built and measured against
`adafruit-circuitpython-ssd1306` 2.12.24 and `adafruit-circuitpython-framebuf`
1.6.12, the same versions PyMCU's own oracle tests pin.

## Build and flash

```bash
pymcu build
pymcu flash          # or: pymcu flash --port /dev/cu.usbmodemXXXX
```

## Verified

Compiles with PyMCU's main-branch compiler to 13126/32768 bytes of flash
(1606 bytes of static SRAM, see above); the I2C traffic it produces
matches, frame for frame (46 frames compared, 0 differences), a plain
CPython run of the same unmodified driver sources against a fake I2C bus
(see the `ssd1306-trace-dump` tool in `pymcu-avr`). This 128x64 version has
not yet been flashed to a real board. An earlier 128x32 version of this
same program did run on a real Arduino Uno with a 128x32 SSD1306 module.

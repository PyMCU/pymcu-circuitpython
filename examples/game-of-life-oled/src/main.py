# Conway's Game of Life on the OLED
# Optimized for CircuitPython, using fill_rect and time.sleep
import time
import board
import adafruit_ssd1306

CELL = 4
SEED = 20260921

# Display initialization
i2c = board.I2C()
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)


class Life:
    """Conway's Game of Life on a toroidal width x height grid of cells."""

    def __init__(self, width, height, seed):
        self.width = width
        self.height = height
        self.cells = [[0] * width for _ in range(height)]
        self.rng = seed

    def seed(self):
        # A small LCG in Python, not the random module.
        for y in range(self.height):
            for x in range(self.width):
                self.rng = (self.rng * 1103515245 + 12345) & 0x7FFFFFFF
                self.cells[y][x] = 1 if ((self.rng >> 16) & 3) == 0 else 0

    def step(self):
        # One grid, not cells + next_cells: at 128x64 the two-grid version
        # needs more SRAM than the Arduino Uno has (2 KB total). Each row is
        # updated in place, but computing a row still needs its neighbours'
        # UNCHANGED values, including the row above, which has already been
        # overwritten by the time we get here. So two rows of backup are
        # kept instead of a whole second grid: prev_row (the row just
        # finished, copied forward one row at a time) and first_row (row 0,
        # saved once up front, needed again at the last row because the
        # board wraps top to bottom).
        w = self.width
        h = self.height
        cells = self.cells

        first_row = [0] * w
        for x in range(w):
            first_row[x] = cells[0][x]

        prev_row = [0] * w
        for x in range(w):
            prev_row[x] = cells[h - 1][x]

        old_row = [0] * w
        changed = 0
        for y in range(h):
            for x in range(w):
                old_row[x] = cells[y][x]

            is_last = y == h - 1
            next_y = 0 if is_last else y + 1

            for x in range(w):
                n = 0
                for dx in range(-1, 2):
                    xx = (x + dx) % w
                    next_value = first_row[xx] if is_last else cells[next_y][xx]
                    n = n + prev_row[xx] + old_row[xx] + next_value
                n = n - old_row[x]
                if old_row[x]:
                    new_value = 1 if n == 2 or n == 3 else 0
                else:
                    new_value = 1 if n == 3 else 0
                if new_value != old_row[x]:
                    changed = 1
                cells[y][x] = new_value

            for x in range(w):
                prev_row[x] = old_row[x]
        return changed

    def alive(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x]:
                    return 1
        return 0

    def draw(self, display):
        display.fill(0)
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x]:
                    # OPTIMIZATION 1: use fill_rect to draw the whole cell at
                    # once instead of looping over it pixel by pixel.
                    display.fill_rect(x * CELL, y * CELL, CELL, CELL, 1)
        display.show()


life = Life(32, 16, SEED)
life.seed()
life.draw(display)
generation = 0

while True:
    tick = time.monotonic()
    changed = life.step()
    life.draw(display)
    generation = generation + 1

    if generation % 10 == 0:
        print("generation", generation)

    if changed == 0 or life.alive() == 0:
        # Dead or frozen world: hold the last frame, then a fresh soup.
        time.sleep(1.0)
        life.seed()
        life.draw(display)
        generation = 0

    # OPTIMIZATION 2: rest the processor instead of spinning in a busy wait.
    elapsed = time.monotonic() - tick
    if elapsed < 0.1:
        time.sleep(0.1 - elapsed)

# Conway's Game of Life on the OLED
# Optimized for CircuitPython, using fill_rect and time.sleep
import time
import board
import adafruit_ssd1306

CELL = 8
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
        self.next_cells = [[0] * width for _ in range(height)]
        self.rng = seed

    def seed(self):
        # A small LCG in Python, not the random module.
        for y in range(self.height):
            for x in range(self.width):
                self.rng = (self.rng * 1103515245 + 12345) & 0x7FFFFFFF
                self.cells[y][x] = 1 if ((self.rng >> 16) & 3) == 0 else 0

    def neighbours(self, x, y):
        n = 0
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                xx = (x + dx) % self.width
                yy = (y + dy) % self.height
                n = n + self.cells[yy][xx]
        return n

    def step(self):
        for y in range(self.height):
            for x in range(self.width):
                n = self.neighbours(x, y)
                if self.cells[y][x]:
                    self.next_cells[y][x] = 1 if n == 2 or n == 3 else 0
                else:
                    self.next_cells[y][x] = 1 if n == 3 else 0
        changed = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] != self.next_cells[y][x]:
                    changed = 1
                self.cells[y][x] = self.next_cells[y][x]
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


life = Life(16, 8, SEED)
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

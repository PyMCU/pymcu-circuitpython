"""Tests for the CircuitPython-compatible neopixel module."""
import pymcu_circuitpython.neopixel as neopixel


def test_construct_and_len():
    pixels = neopixel.NeoPixel("PD6", 8)
    assert len(pixels) == 8
    assert pixels.n == 8


def test_fill_tuple_sets_every_pixel():
    # CircuitPython idiom: fill with an (r, g, b) tuple.
    calls = []

    class _RecordingStrip:
        def __init__(self, pin, n):
            self._n = n

        def set_pixel(self, r, g, b):
            calls.append((r, g, b))

        def show(self):
            calls.append("show")

    pixels = neopixel.NeoPixel("PD6", 3)
    pixels._strip = _RecordingStrip("PD6", 3)
    pixels.fill((255, 0, 0))

    assert calls.count((255, 0, 0)) == 3, "fill should set all 3 pixels red"
    assert "show" in calls, "fill should latch the strip"


def test_auto_write_default_true():
    pixels = neopixel.NeoPixel("PD6", 1)
    assert pixels.auto_write == 1


def test_colour_order_constants():
    assert neopixel.RGB == "RGB"
    assert neopixel.GRB == "GRB"
    assert neopixel.RGBW == "RGBW"
    assert neopixel.GRBW == "GRBW"


def test_setitem_is_noop_stub():
    # __setitem__ is a documented @warning stub (needs an instance framebuffer);
    # in CPython it is simply a no-op passthrough and must not raise.
    pixels = neopixel.NeoPixel("PD6", 4)
    pixels[0] = (0, 255, 0)

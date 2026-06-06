"""Tests for the CircuitPython-compatible neopixel module."""
import pymcu_circuitpython.neopixel as neopixel


def test_construct_and_len():
    pixels = neopixel.NeoPixel("PD6", 8)
    assert len(pixels) == 8
    assert pixels.n == 8


def test_fill_tuple_writes_framebuffer_grb():
    # CircuitPython idiom: fill with an (r, g, b) tuple. The framebuffer is in
    # WS2812 wire (GRB) order, so red (255, 0, 0) -> bytes G=0, R=255, B=0.
    pixels = neopixel.NeoPixel("PD6", 3)
    pixels.fill((255, 0, 0))
    assert list(pixels._buf) == [0, 255, 0] * 3


def test_setitem_tuple_writes_single_pixel_grb():
    # pixels[i] = (r, g, b) writes one pixel into the framebuffer (GRB order).
    pixels = neopixel.NeoPixel("PD6", 4)
    pixels[2] = (10, 20, 30)  # R=10, G=20, B=30 -> buf[6:9] = [G, R, B]
    assert list(pixels._buf[6:9]) == [20, 10, 30]
    # Untouched pixels stay zero.
    assert list(pixels._buf[0:6]) == [0, 0, 0, 0, 0, 0]


def test_auto_write_default_true():
    pixels = neopixel.NeoPixel("PD6", 1)
    assert pixels.auto_write == 1


def test_colour_order_constants():
    assert neopixel.RGB == "RGB"
    assert neopixel.GRB == "GRB"
    assert neopixel.RGBW == "RGBW"
    assert neopixel.GRBW == "GRBW"

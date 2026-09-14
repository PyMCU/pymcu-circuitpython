"""rainbowio: the colour at a position on the wheel (#15).

The module was absent, so every example that colours a strip by position carried its own
wheel().
"""
from pymcu_circuitpython.rainbowio import colorwheel


def test_the_corners_are_the_three_primaries():
    assert colorwheel(0) == 0xFF0000, "red"
    assert colorwheel(85) == 0x00FF00, "green"
    assert colorwheel(170) == 0x0000FF, "blue"


def test_between_two_corners_one_channel_falls_while_the_next_rises():
    # pos 42 is halfway from red to green: 255 - 42*3 and 42*3.
    assert colorwheel(42) == (129 << 16) | (126 << 8)
    # pos 127 is halfway from green to blue: pos - 85 is 42.
    assert colorwheel(127) == (129 << 8) | 126
    # pos 212 is halfway from blue to red: pos - 170 is 42.
    assert colorwheel(212) == (126 << 16) | 129


def test_every_position_keeps_one_channel_dark():
    # The wheel walks the edges of the colour cube: two channels at a time, never three.
    for pos in range(256):
        c = colorwheel(pos)
        channels = [(c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF]
        assert channels.count(0) >= 1, pos


def test_the_two_lit_channels_always_add_to_255():
    for pos in range(256):
        c = colorwheel(pos)
        assert ((c >> 16) & 0xFF) + ((c >> 8) & 0xFF) + (c & 0xFF) == 255, pos

"""`neopixel_write(digitalinout, buf)`, the call below the neopixel library (#14).

What is checked here is the shape a layer owns: which pin the bytes go to, in which
order, and that the frame is opened and latched. The bit times are the protocol and are
cycles, so they are measured where cycles exist -- pymcu-avr,
fixtures/compat-cp-neopixel-write, which reads the waveform off PD6 and decodes it back
into these same bytes.
"""

import sys

import pytest

import digitalio
import neopixel_write


@pytest.fixture
def wire():
    """What reached the emitter, cleared for each test."""
    log = sys.modules["pymcu.hal.ws2812"].log
    log.clear()
    return log


def _output(pin):
    dio = digitalio.DigitalInOut(pin)
    dio.direction = digitalio.Direction.OUTPUT
    return dio


def test_the_bytes_reach_the_pin_the_digitalinout_was_built_on(wire):
    neopixel_write.neopixel_write(_output("PD6"), bytearray([1, 2, 3]))

    assert [entry for entry in wire if entry[0] == "byte"] == [
        ("byte", "PD6", 1), ("byte", "PD6", 2), ("byte", "PD6", 3)]


def test_the_buffer_is_not_reordered(wire):
    """A WS2812 takes green, red, blue, and that ordering is the caller's to make.

    CircuitPython's neopixel_write does not touch the buffer either. Reordering here
    would put a second opinion between a caller and the wire, and the caller is the one
    that knows whether the strip is a GRB part or an RGBW one.
    """
    neopixel_write.neopixel_write(_output("PB3"), bytearray([0x00, 0xFF, 0xA5]))

    assert [entry[2] for entry in wire if entry[0] == "byte"] == [0x00, 0xFF, 0xA5]


def test_the_frame_is_opened_and_latched(wire):
    neopixel_write.neopixel_write(_output("PD6"), bytearray([7]))

    assert wire[0] == ("init", "PD6"), "the line is driven low before the first bit"
    assert wire[-1] == ("reset", "PD6"), "and held low past 50 us so the strip latches"


def test_an_empty_buffer_still_latches(wire):
    """No bytes is not no call: a strip that was sent nothing still ends its frame."""
    neopixel_write.neopixel_write(_output("PD6"), bytearray())

    assert [entry[0] for entry in wire] == ["init", "reset"]


def test_a_second_write_goes_to_its_own_pin(wire):
    """Two strips on two legs. The pin comes off the DigitalInOut, not from anywhere global."""
    neopixel_write.neopixel_write(_output("PD6"), bytearray([1]))
    neopixel_write.neopixel_write(_output("PB1"), bytearray([2]))

    assert [entry for entry in wire if entry[0] == "byte"] == [
        ("byte", "PD6", 1), ("byte", "PB1", 2)]

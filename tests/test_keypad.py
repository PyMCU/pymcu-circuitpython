"""keypad: which button changed, and which way (#13).

The module was absent. There is no HAL half: a keypad is digitalio and bookkeeping.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython import digitalio
from pymcu_circuitpython.keypad import Keys, Event


def _keys(n=3):
    pins = [digitalio.DigitalInOut(f"PD{4 + i}") for i in range(n)]
    for p in pins:
        p.switch_to_input(pull=digitalio.Pull.UP)
        p._pin._v = 1          # idle high through the pull-up
    return Keys(pins, value_when_pressed=False), pins


def _press(pin):
    pin._pin._v = 0


def _release(pin):
    pin._pin._v = 1


def test_the_key_count_is_the_number_of_pins_given():
    keys, _ = _keys(3)
    assert keys.key_count == 3


def test_nothing_pressed_is_no_event():
    keys, _ = _keys()
    event = Event()
    assert keys.events.get_into(event) == 0
    assert len(keys.events) == 0


def test_one_press_is_one_event_and_then_nothing():
    keys, pins = _keys()
    event = Event()
    _press(pins[1])
    assert keys.events.get_into(event) == 1
    assert (event.key_number, event.pressed) == (1, 1)
    assert keys.events.get_into(event) == 0


def test_a_release_is_an_event_too():
    keys, pins = _keys()
    event = Event()
    _press(pins[0])
    keys.events.get_into(event)
    _release(pins[0])
    assert keys.events.get_into(event) == 1
    assert (event.key_number, event.pressed) == (0, 0)
    assert event.released == 1


def test_two_presses_come_out_one_at_a_time_in_pin_order():
    keys, pins = _keys()
    event = Event()
    _press(pins[0])
    _press(pins[2])
    assert len(keys.events) == 2
    assert keys.events.get_into(event) == 1 and event.key_number == 0
    assert len(keys.events) == 1
    assert keys.events.get_into(event) == 1 and event.key_number == 2
    assert len(keys.events) == 0


def test_clear_forgets_what_has_not_been_read():
    keys, pins = _keys()
    event = Event()
    _press(pins[1])
    keys.events.clear()
    assert len(keys.events) == 0
    assert keys.events.get_into(event) == 0


def test_the_queue_cannot_overflow_because_it_holds_nothing():
    keys, _ = _keys()
    assert keys.events.overflowed == 0


def test_get_says_what_to_use_instead():
    keys, _ = _keys()
    with pytest.raises(CompileError) as e:
        keys.events.get()
    assert "get_into" in str(e.value)


def test_interval_and_max_events_are_refused_rather_than_dropped():
    pins = [digitalio.DigitalInOut("PD4")]
    with pytest.raises(CompileError) as e:
        Keys(pins, interval=20)
    assert "background" in str(e.value)
    with pytest.raises(CompileError) as e:
        Keys(pins, max_events=64)
    assert "nothing to size" in str(e.value)


def test_more_than_thirty_two_keys_is_refused():
    pins = [digitalio.DigitalInOut("PD4") for _ in range(33)]
    with pytest.raises(CompileError):
        Keys(pins)

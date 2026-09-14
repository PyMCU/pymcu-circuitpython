"""pwmio: PWMOut duty_cycle (16-bit) and frequency."""
from pymcu_circuitpython.pwmio import PWMOut


def test_duty_cycle_roundtrip():
    p = PWMOut("PD6", duty_cycle=32768)
    assert p.duty_cycle == 32768
    p.duty_cycle = 49152
    assert p.duty_cycle == 49152


def test_frequency_reports_what_the_pin_emits():
    # It used to report the request. On a timer whose period is fixed at 256 counts the
    # frequencies on offer are a handful of buckets, so 1000 Hz on Timer0 comes out at 976
    # and 5000 at 7812 (#18).
    assert PWMOut("PD6", frequency=1000).frequency == 976
    assert PWMOut("PD6", frequency=5000).frequency == 7812


def test_a_timer1_pin_honours_the_frequency_exactly():
    # A Timer1 channel asking for something that is not one of the buckets reaches the mode
    # whose period is a register, which is what makes the 50 Hz servo idiom work (#8).
    assert PWMOut("PB1", frequency=50).frequency == 50
    assert PWMOut("PB2", frequency=1000).frequency == 1000


def test_the_first_parameter_is_named_pin():
    # It was pin_name, so PWMOut(pin=board.D9, ...) -- the keyword form every Adafruit guide
    # uses -- did not compile (#18).
    assert PWMOut(pin="PD6", frequency=1000).frequency == 976


def test_context_manager():
    with PWMOut("PD6", duty_cycle=0) as p:
        p.duty_cycle = 100


def test_frequency_setter_reprograms_the_timer():
    from pymcu.exceptions import CompileError
    import pytest

    # The frequency read back is the one the PIN emits, not the one asked for: on a timer
    # whose period is fixed at 256 counts the frequencies on offer are a handful of buckets
    # (#18). 20000 Hz on Timer0 is the 7812 Hz bucket.
    p = PWMOut("PD6", frequency=1000, variable_frequency=True)
    assert p.frequency == 976, "1000 Hz on Timer0 is the 976 Hz bucket"
    p.frequency = 20000
    assert p.frequency == 7812

    fixed = PWMOut("PD6", frequency=1000)
    with pytest.raises(CompileError):
        fixed.frequency = 20000


def test_deinit_releases_the_pin(monkeypatch):
    # PyMCU#296: deinit() has to reach the HAL's deinit(), which disconnects the compare
    # output, drives the pin low and returns it to an input. Stopping the timer is not
    # it: that freezes the sibling channel and the time base, and leaves the pin at
    # whatever level the compare latch had.
    import pymcu_circuitpython.pwmio as pwmio_mod

    calls: list = []

    class _Recorder(pwmio_mod._PWM):
        def deinit(self):
            calls.append("deinit")
        def stop(self):
            calls.append("stop")

    monkeypatch.setattr(pwmio_mod, "_PWM", _Recorder)
    p = PWMOut("PD6", duty_cycle=32768)
    p.deinit()
    assert calls == ["deinit"]

    calls.clear()
    with PWMOut("PD6", duty_cycle=32768):
        pass
    assert calls == ["deinit"], "the context manager exit is a deinit()"

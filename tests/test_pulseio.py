"""pulseio: PulseIn measures the pulses on a pin, PulseOut sends a gated carrier (#9).

The module did not exist, so the two things it is for -- an infrared receiver and a DHT on
any digital pin -- had no way into the layer at all.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.pulseio import PulseIn, PulseOut


def test_a_pulse_in_starts_empty():
    pulses = PulseIn("PD2", maxlen=8)
    assert len(pulses) == 0
    assert pulses[0] == 0, "an index past the end reads as zero"


def test_pulses_come_out_oldest_first():
    pulses = PulseIn("PD2", maxlen=8)
    pulses._cap.feed(9000, 4500, 560, 1690)
    assert len(pulses) == 4
    assert pulses[0] == 9000
    assert pulses[1] == 4500
    assert pulses.popleft() == 9000
    assert pulses.popleft() == 4500
    assert len(pulses) == 2
    assert pulses[0] == 560


def test_maxlen_is_what_was_asked_for_and_bounds_the_queue():
    pulses = PulseIn("PD2", maxlen=3)
    assert pulses.maxlen == 3
    pulses._cap.feed(1, 2, 3, 4, 5)
    assert len(pulses) == 3, "a pulse that arrives with the buffer full is dropped"


def test_a_maxlen_bigger_than_the_buffer_is_refused():
    with pytest.raises(CompileError):
        PulseIn("PD2", maxlen=256)


def test_a_maxlen_of_zero_is_refused():
    with pytest.raises(CompileError):
        PulseIn("PD2", maxlen=0)


def test_clear_empties_the_queue():
    pulses = PulseIn("PD2", maxlen=8)
    pulses._cap.feed(560, 560)
    pulses.clear()
    assert len(pulses) == 0


def test_pause_stops_recording_and_resume_starts_it():
    pulses = PulseIn("PD2", maxlen=8)
    pulses.pause()
    assert pulses.paused == 1
    pulses._cap.feed(560, 560)
    assert len(pulses) == 0, "pulses that arrive while paused are lost, not queued"
    pulses.resume()
    assert pulses.paused == 0
    pulses._cap.feed(560)
    assert len(pulses) == 1


def test_resume_with_a_trigger_duration_says_what_to_do_instead():
    # The pin is an input while it is being measured, so there is nothing to drive. Refusing
    # is the alternative to accepting the duration and dropping it.
    pulses = PulseIn("PD2", maxlen=8)
    with pytest.raises(CompileError) as e:
        pulses.resume(trigger_duration=100)
    assert "digitalio" in str(e.value)
    pulses.resume()


def test_a_pulse_out_carries_the_frequency_and_duty_to_the_hal():
    out = PulseOut("PD3", frequency=38000, duty_cycle=16384)
    assert (out._train.freq, out._train.duty) == (38000, 16384)


def test_a_pulse_out_on_a_pin_with_no_carrier_channel_is_refused():
    with pytest.raises(CompileError) as e:
        PulseOut("PB1", frequency=38000)
    assert "PD3" in str(e.value)


def test_a_carrier_frequency_the_timer_cannot_reach_is_refused():
    with pytest.raises(CompileError):
        PulseOut("PD3", frequency=1000)


def test_send_passes_the_durations_through():
    out = PulseOut("PD3")
    out.send([9000, 4500, 560, 1690], 4)
    assert out._train.sent == [9000, 4500, 560, 1690]


def test_send_takes_only_the_count_it_was_given():
    out = PulseOut("PD3")
    out.send([560, 560, 1690, 560], 2)
    assert out._train.sent == [560, 560]

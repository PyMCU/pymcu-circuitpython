"""rotaryio: where a two-track knob has turned to (#12).

The module was absent, so a panel knob had no way into the layer. It is also the module
that found PyMCU#328: a global shared between an interrupt handler and the main program was
allocated in the callee-saved pool R2-R15, and every handler's epilogue restored it, undoing
the write the handler had just made. The position never moved. These tests run under CPython
and cannot see that; the fixture in pymcu-avr can, and does.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.rotaryio import IncrementalEncoder


# One detent of a common knob, in the order the two lines change. A knob idles with both
# lines released, which with the pull-ups on reads high, so a detent starts and ends at 1, 1.
FORWARD = ((1, 0), (0, 0), (0, 1), (1, 1))
BACKWARD = ((0, 1), (0, 0), (1, 0), (1, 1))


def turn(knob, sequence, times=1):
    for _ in range(times):
        for a, b in sequence:
            knob._q.lines(a, b)


def test_a_knob_starts_where_it_is():
    assert IncrementalEncoder("PD2", "PD3").position == 0


def test_the_idle_lines_are_not_a_first_step():
    # The decoder is primed from the lines. Started at 00, the first edge of a knob that
    # idles at 11 looked like a step that never happened.
    knob = IncrementalEncoder("PD2", "PD3")
    knob._q.lines(1, 1)
    assert knob._q.position() == 0


def test_eight_quarter_steps_are_two_detents():
    # The measurement the whole module exists for: four line changes per click.
    knob = IncrementalEncoder("PD2", "PD3")
    turn(knob, FORWARD, times=2)
    assert knob._q.position() == 8
    assert knob.position == 2


def test_turning_the_other_way_counts_down():
    knob = IncrementalEncoder("PD2", "PD3")
    turn(knob, FORWARD, times=2)
    turn(knob, BACKWARD, times=3)
    assert knob._q.position() == -4
    assert knob.position == -1


def test_a_partial_detent_is_not_a_detent_yet():
    knob = IncrementalEncoder("PD2", "PD3")
    knob._q.lines(1, 0)
    knob._q.lines(0, 0)
    assert knob._q.position() == 2
    assert knob.position == 0


def test_rounding_is_towards_zero_so_one_click_back_reads_minus_one():
    knob = IncrementalEncoder("PD2", "PD3")
    turn(knob, BACKWARD)
    assert knob.position == -1


def test_a_bounce_that_changes_both_lines_at_once_is_not_a_direction():
    knob = IncrementalEncoder("PD2", "PD3")
    knob._q.lines(0, 0)          # from 11 straight to 00: an edge was missed
    assert knob._q.position() == 0


def test_nothing_changing_is_not_a_direction():
    knob = IncrementalEncoder("PD2", "PD3")
    knob._q.lines(1, 0)
    knob._q.lines(1, 0)
    assert knob._q.position() == 1


def test_divisor_two_makes_every_other_change_a_detent():
    knob = IncrementalEncoder("PD2", "PD3", divisor=2)
    turn(knob, FORWARD, times=2)
    assert knob.position == 4


def test_divisor_one_counts_every_change():
    knob = IncrementalEncoder("PD2", "PD3", divisor=1)
    turn(knob, FORWARD, times=2)
    assert knob.position == 8


def test_a_divisor_that_describes_no_knob_is_refused():
    with pytest.raises(CompileError):
        IncrementalEncoder("PD2", "PD3", divisor=3)


def test_the_position_can_be_moved_and_counting_goes_on_from_there():
    knob = IncrementalEncoder("PD2", "PD3")
    knob.position = 10
    assert knob._q.position() == 40
    turn(knob, FORWARD)
    assert knob.position == 11


def test_divisor_reports_what_was_asked_for():
    assert IncrementalEncoder("PD2", "PD3", divisor=2).divisor == 2


def test_changing_the_divisor_afterwards_is_refused_and_names_the_constructor():
    knob = IncrementalEncoder("PD2", "PD3")
    with pytest.raises(CompileError) as e:
        knob.divisor = 2
    assert "constructor" in str(e.value)


def test_two_lines_on_different_ports_are_refused():
    # The handler reads one port register, and a register address is fixed when the firmware
    # is built.
    with pytest.raises(CompileError):
        IncrementalEncoder("PD2", "PB0")


def test_the_same_pin_twice_is_refused():
    with pytest.raises(CompileError):
        IncrementalEncoder("PD2", "PD2")


def test_deinit_puts_it_back_to_zero():
    knob = IncrementalEncoder("PD2", "PD3")
    turn(knob, FORWARD)
    knob.deinit()
    assert knob.position == 0


def test_it_works_as_a_context_manager():
    with IncrementalEncoder("PD2", "PD3") as knob:
        turn(knob, FORWARD)
        assert knob.position == 1
    assert knob.position == 0

"""countio: how many edges arrived on a pin (#11).

The module was absent, so a flow meter or a tachometer had no way into the layer.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.countio import Counter, Edge


def test_a_counter_starts_at_zero():
    assert Counter("PD2").count == 0


def test_every_edge_is_counted():
    c = Counter("PD2", edge=Edge.FALL)
    c._counter.tick(5)
    assert c.count == 5


def test_reset_puts_it_back_to_zero():
    c = Counter("PD2")
    c._counter.tick(5)
    c.reset()
    assert c.count == 0


def test_assigning_zero_to_count_clears_it():
    c = Counter("PD2")
    c._counter.tick(3)
    c.count = 0
    assert c.count == 0


def test_assigning_anything_else_to_count_is_refused():
    # A counter counts edges as they arrive and there is nowhere to start it from.
    c = Counter("PD2")
    with pytest.raises(CompileError):
        c.count = 100


def test_the_edge_numbers_are_the_hals():
    assert (Edge.RISE_AND_FALL, Edge.RISE, Edge.FALL) == (0, 1, 2)
    assert Counter("PD2", edge=Edge.RISE)._counter.edge == 1


def test_a_single_edge_on_a_pin_that_cannot_tell_them_apart_is_refused():
    # Only INT0 and INT1 select an edge in hardware; the rest fire on both.
    with pytest.raises(CompileError) as e:
        Counter("PD7", edge=Edge.FALL)
    assert "INT0" in str(e.value)
    Counter("PD7", edge=Edge.RISE_AND_FALL)


def test_the_pull_up_is_on_unless_the_program_says_otherwise():
    # The thing being counted is usually a switch or an open-collector sensor pulling down.
    assert Counter("PD2")._counter.pull == 1
    assert Counter("PD2", pull=0)._counter.pull == 0

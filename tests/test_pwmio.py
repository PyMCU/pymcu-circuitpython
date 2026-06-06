"""pwmio: PWMOut duty_cycle (16-bit) and frequency."""
from pymcu_circuitpython.pwmio import PWMOut


def test_duty_cycle_roundtrip():
    p = PWMOut("PD6", duty_cycle=32768)
    assert p.duty_cycle == 32768
    p.duty_cycle = 49152
    assert p.duty_cycle == 49152


def test_frequency():
    p = PWMOut("PD6", frequency=1000)
    assert p.frequency == 1000


def test_context_manager():
    with PWMOut("PD6", duty_cycle=0) as p:
        p.duty_cycle = 100

"""adafruit_motor.servo: the servo idiom (#8).

pwmio.PWMOut(board.D9, frequency=50) into a Servo, and an angle that lands on the pulse
width it names. It did not work: Timer1's eight-bit fast PWM has five frequencies and 50 Hz
ran at 61, while PWMOut.frequency reported the 50 that was asked for.
"""
import pytest
from pymcu.exceptions import CompileError
from pymcu_circuitpython.pwmio import PWMOut
from pymcu_circuitpython.adafruit_motor.servo import Servo, ContinuousServo


def _servo(**kw):
    return Servo(PWMOut("PB1", frequency=50), min_pulse=1000, max_pulse=2000, **kw)


def test_the_pwm_runs_at_the_frequency_a_servo_needs():
    assert PWMOut("PB1", frequency=50).frequency == 50


def test_the_ends_of_travel_are_the_pulse_widths_asked_for():
    s = _servo()
    # 1000 us of a 20 000 us period is 3276 of 65535; 2000 us is 6553.
    assert s._period == 20000
    assert s._min_duty == 3276
    assert s._max_duty == 6553


def test_an_angle_lands_on_its_pulse_width():
    s = _servo()
    for angle, duty in ((0, 3276), (90, 4914), (180, 6553)):
        s.angle = angle
        assert s._pwm.duty_cycle == duty, angle
        assert s.angle == angle


def test_an_angle_past_the_end_of_travel_is_refused():
    s = _servo()
    with pytest.raises(CompileError):
        s.angle = 200


def test_a_wider_actuation_range_accepts_a_wider_angle():
    s = _servo(actuation_range=270)
    s.angle = 270
    assert s._pwm.duty_cycle == 6553


def test_fraction_walks_the_same_range():
    s = _servo()
    s.fraction = 0
    assert s._pwm.duty_cycle == 3276
    s.fraction = 65535
    assert s._pwm.duty_cycle == 6553


def test_set_pulse_width_range_moves_the_ends():
    s = _servo()
    s.set_pulse_width_range(500, 2500)
    assert s._min_duty == 1638
    assert s._max_duty == 8191


def test_a_continuous_servo_stops_at_the_midpoint():
    c = ContinuousServo(PWMOut("PB1", frequency=50), min_pulse=1000, max_pulse=2000)
    c.throttle = 0
    assert c._pwm.duty_cycle == pytest.approx(4914, abs=2)
    c.throttle = -32768
    assert c._pwm.duty_cycle == 3276
    c.throttle = 32767
    assert c._pwm.duty_cycle == pytest.approx(6553, abs=2)

from pymcu_circuitpython.pwmio import PWMOut


def test_pwmout_instantiation():
    pwm = PWMOut("PD6")
    assert pwm is not None


def test_pwmout_default_duty_cycle():
    pwm = PWMOut("PD6", duty_cycle=0)
    assert pwm.duty_cycle == 0


def test_pwmout_initial_duty_cycle_stored():
    pwm = PWMOut("PD6", duty_cycle=32768)
    assert pwm.duty_cycle == 32768


def test_pwmout_set_duty_cycle():
    pwm = PWMOut("PD6")
    pwm.duty_cycle = 49152
    assert pwm.duty_cycle == 49152


def test_pwmout_duty_cycle_zero():
    pwm = PWMOut("PD6", duty_cycle=65535)
    pwm.duty_cycle = 0
    assert pwm.duty_cycle == 0


def test_pwmout_duty_cycle_max():
    pwm = PWMOut("PD6")
    pwm.duty_cycle = 65535
    assert pwm.duty_cycle == 65535


def test_pwmout_deinit():
    pwm = PWMOut("PD6")
    pwm.deinit()  # should not raise

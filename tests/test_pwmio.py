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


def test_frequency_default():
    pwm = PWMOut("PD6")
    assert pwm.frequency == 500


def test_frequency_custom():
    pwm = PWMOut("PD6", frequency=1000)
    assert pwm.frequency == 1000


def test_frequency_setter():
    pwm = PWMOut("PD6", variable_frequency=1)
    pwm.frequency = 2000
    assert pwm.frequency == 2000


def test_variable_frequency_default_false():
    pwm = PWMOut("PD6")
    assert pwm.variable_frequency == 0


def test_variable_frequency_true():
    pwm = PWMOut("PD6", variable_frequency=1)
    assert pwm.variable_frequency == 1


def test_enabled():
    pwm = PWMOut("PD6")
    assert pwm.enabled == 1


def test_context_manager():
    pwm = PWMOut("PD6")
    pwm.__enter__()
    pwm.__exit__()  # calls deinit; must not raise

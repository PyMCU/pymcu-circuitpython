"""alarm: waiting on more than one alarm, and knowing which fired (#20).

light_sleep_until_alarms() took one alarm and returned a constant 0, so a program waiting on
"a time limit or a button" could only wait on one of the two.
"""
from unittest.mock import patch
import pymcu_circuitpython.alarm as alarm


def _millis_reaching(*values):
    """A millis() that walks the given readings, then stays at the last."""
    seq = list(values)

    def _m():
        return seq.pop(0) if len(seq) > 1 else seq[0]
    return _m


def test_a_time_alarm_keeps_its_deadline_in_whole_milliseconds():
    # The soft-float arithmetic happens once at construction, not on every pass of the loop.
    ta = alarm.time.TimeAlarm(monotonic_time=1.5)
    assert ta._deadline_ms == 1500
    assert ta._is_time == 1


def test_alarm_time_and_alarm_pin_are_modules_not_instances():
    # Upstream alarm.time / alarm.pin are real submodules
    # (`import alarm.time` / `alarm.time.TimeAlarm`); the layer used to answer
    # singleton instances, a shape a board never produces.
    import types
    assert isinstance(alarm.time, types.ModuleType)
    assert isinstance(alarm.pin, types.ModuleType)
    import pymcu_circuitpython.alarm.time
    import pymcu_circuitpython.alarm.pin


def test_a_pin_alarm_carries_the_fields_a_time_alarm_has_and_the_other_way_round():
    # A mixed set of alarms is polled in one loop, so both types answer the same questions.
    ta = alarm.time.TimeAlarm(monotonic_time=1.0)
    pa = alarm.pin.PinAlarm("PD2", value=True)
    for a in (ta, pa):
        assert hasattr(a, "_is_time") and hasattr(a, "_deadline_ms")
        assert hasattr(a, "_pin_name") and hasattr(a, "_value")


def test_the_first_alarm_to_fire_is_the_one_reported():
    import pymcu.hal.timer as _t
    ta = alarm.time.TimeAlarm(monotonic_time=0.05)
    pa = alarm.pin.PinAlarm("PD2", value=1)
    with patch.object(_t, "millis", _millis_reaching(0, 10, 60)):
        # The pin reads 0 from the mock, so only the time alarm can fire.
        assert alarm.light_sleep_until_alarms(ta, pa) == 0


def test_a_pin_alarm_later_in_the_list_reports_its_own_position():
    import pymcu.hal.timer as _t
    ta = alarm.time.TimeAlarm(monotonic_time=1000.0)
    pa = alarm.pin.PinAlarm("PD2", value=0)     # the mock pin reads 0, so this fires at once
    with patch.object(_t, "millis", _millis_reaching(0)):
        assert alarm.light_sleep_until_alarms(ta, pa) == 1


def test_a_single_alarm_still_works_and_reports_zero():
    import pymcu.hal.timer as _t
    ta = alarm.time.TimeAlarm(monotonic_time=0.01)
    with patch.object(_t, "millis", _millis_reaching(0, 50)):
        assert alarm.light_sleep_until_alarms(ta) == 0


def test_more_alarms_than_the_old_four_positional_limit_are_accepted():
    # Upstream spells it *alarms; the old four-fixed-positionals signature could
    # not take a fifth alarm. The pin fires at once, so five is where it lands.
    import pymcu.hal.timer as _t
    alarms = [alarm.time.TimeAlarm(monotonic_time=1000.0) for _ in range(4)]
    alarms.append(alarm.pin.PinAlarm("PD2", value=0))
    with patch.object(_t, "millis", _millis_reaching(0)):
        assert alarm.light_sleep_until_alarms(*alarms) == 4


def test_exit_and_deep_sleep_takes_alarms_and_preserve_dios_like_upstream():
    import pymcu.hal.timer as _t
    ta = alarm.time.TimeAlarm(monotonic_time=0.01)
    pa = alarm.pin.PinAlarm("PD2", value=0)
    with patch.object(_t, "millis", _millis_reaching(0)):
        assert alarm.exit_and_deep_sleep_until_alarms(ta, pa, preserve_dios=()) == 1


def test_the_invented_sleep_until_alarms_spelling_is_gone():
    # Upstream has only light_sleep_until_alarms and exit_and_deep_sleep_until_alarms;
    # a name that exists here but not on a board is the failure the layer exists to prevent.
    assert not hasattr(alarm, "sleep_until_alarms")


def test_wake_alarm_is_none_and_says_why():
    # CircuitPython puts the alarm object there; an instance cannot live in a module global
    # here, so the position comes back from the call instead.
    assert alarm.wake_alarm is None

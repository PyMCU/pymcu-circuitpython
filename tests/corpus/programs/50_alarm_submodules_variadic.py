# expect: build
# source: CircuitPython alarm docs; *alarms signature and real alarm.time/alarm.pin
# submodules measured on CircuitPython 10.3.1 (layer-fidelity campaign).
# PyMCU#443: NestedKeywordAlarmTests covers the time deadline; this probe covers
# the module shape and the variadic signature upstream has and ours did not.
import alarm
from alarm.time import TimeAlarm
from alarm.pin import PinAlarm
import alarm.pin
import time
import board

a1 = TimeAlarm(monotonic_time=time.monotonic() + 60)
a2 = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 90)
p1 = PinAlarm(pin=board.D2, value=False, pull=True)
p2 = alarm.pin.PinAlarm(pin=board.D3, value=True)
p3 = alarm.pin.PinAlarm(pin=board.D4, value=True)

# Five alarms: the old four-fixed-positionals signature could not take this call.
wake = alarm.light_sleep_until_alarms(a1, a2, p1, p2, p3)
print(wake)

# Deep-sleep spelling, with upstream's preserve_dios keyword.
fired = alarm.exit_and_deep_sleep_until_alarms(a1, p1, preserve_dios=())
print(fired)

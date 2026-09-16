# expect: build
# source: CircuitPython alarm TimeAlarm docs sleep-until style
# PyMCU#443: the deadline keeps its uint32 width. NestedKeywordAlarmTests in
# pymcu-avr checks that this keyword call waits five seconds, not 136 ms.
import alarm
import time

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
fired = alarm.sleep_until_alarms(time_alarm)
print(fired)

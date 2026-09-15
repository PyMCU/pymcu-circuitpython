# expect: refuse name 'alarm0' is not defined
# source: CircuitPython alarm TimeAlarm docs sleep-until style
import alarm
import time

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
fired = alarm.sleep_until_alarms(time_alarm)
print(fired)

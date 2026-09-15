# expect: refuse name 'alarm0' is not defined
# source: CircuitPython alarm TimeAlarm docs sleep-until style
# note: as of 2026-09-15 this no longer refuses at compile time (something else fixed the
# 'alarm0' resolution bug), but do NOT flip this to "build": the compiled program is
# wrongcode. Verified in avr8sharp: TimeAlarm(monotonic_time=time.monotonic() + 5) fires
# after ~130 ms instead of 5 s. Root cause isolated and filed as PyMCU/PyMCU#443 (a keyword
# argument to a nested class's constructor computes wrong once stored in a field; positional
# calls are correct). Leave failing here until #443 is fixed, then flip and measure.
import alarm
import time

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
fired = alarm.sleep_until_alarms(time_alarm)
print(fired)

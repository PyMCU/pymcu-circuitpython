# expect: refuse name 'alarm0' is not defined
# source: CircuitPython alarm docs multiple alarm wait style
# note: as of 2026-09-15 this no longer refuses at compile time, but do NOT flip this to
# "build": TimeAlarm(monotonic_time=...) is the same wrongcode as 18_alarm_time.py, filed as
# PyMCU/PyMCU#443. Leave failing here until #443 is fixed, then flip and measure.
import time
import board
import alarm

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
pin_alarm = alarm.pin.PinAlarm(pin=board.D2, value=False, pull=True)
wake = alarm.sleep_until_alarms(time_alarm, pin_alarm)
print(wake)

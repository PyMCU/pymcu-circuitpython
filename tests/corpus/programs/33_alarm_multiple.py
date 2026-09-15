# expect: refuse name 'alarm0' is not defined
# source: CircuitPython alarm docs multiple alarm wait style
import time
import board
import alarm

time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 60)
pin_alarm = alarm.pin.PinAlarm(pin=board.D2, value=False, pull=True)
wake = alarm.sleep_until_alarms(time_alarm, pin_alarm)
print(wake)

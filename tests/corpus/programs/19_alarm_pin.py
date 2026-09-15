# expect: build
# source: CircuitPython alarm PinAlarm docs button wake style
import board
import alarm

pin_alarm = alarm.pin.PinAlarm(pin=board.D2, value=False, pull=True)
fired = alarm.sleep_until_alarms(pin_alarm)
print(fired)

# expect: refuse unknown keyword argument 'pull'
# source: CircuitPython keypad.Keys docs polling style
import time
import board
import keypad

keys = keypad.Keys((board.D2, board.D3), value_when_pressed=False, pull=True)

while True:
    event = keys.events.get()
    if event:
        print(event.key_number, event.pressed)
    time.sleep(0.01)

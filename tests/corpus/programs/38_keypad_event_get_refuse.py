# expect: refuse unknown keyword argument 'pull'
# source: CircuitPython keypad EventQueue.get docs style
import time
import board
import keypad

keys = keypad.Keys((board.D2, board.D3), value_when_pressed=False, pull=True)

while True:
    event = keys.events.get()
    if event and event.pressed:
        print(event.key_number)
    time.sleep(0.01)

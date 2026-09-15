# expect: build
# source: CircuitPython pulseio PulseIn docs infrared receiver style
import time
import board
import pulseio

pulses = pulseio.PulseIn(board.D2, maxlen=16, idle_state=True)

while True:
    if len(pulses) >= 4:
        print(pulses[0], pulses[1], pulses[2], pulses[3])
        pulses.clear()
    time.sleep(0.01)

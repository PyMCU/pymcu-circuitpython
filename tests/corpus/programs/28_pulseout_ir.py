# expect: refuse Bit index must be constant for reading
# source: CircuitPython pulseio PulseOut docs infrared carrier style
import time
import board
import pulseio

pulse = pulseio.PulseOut(board.D3, frequency=38000, duty_cycle=32768)
signal = [9000, 4500, 560, 560, 560, 1690]

while True:
    pulse.send(signal, len(signal))
    time.sleep(1)

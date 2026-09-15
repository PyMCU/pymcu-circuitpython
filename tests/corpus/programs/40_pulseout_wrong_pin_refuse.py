# expect: refuse a pulse train's carrier comes out of OC2B
# source: CircuitPython pulseio PulseOut docs shape on an arbitrary PWM-capable pin
import time
import board
import pulseio

pulse = pulseio.PulseOut(board.D9, frequency=38000, duty_cycle=32768)
signal = [9000, 4500, 560, 560]

while True:
    pulse.send(signal, len(signal))
    time.sleep(1)

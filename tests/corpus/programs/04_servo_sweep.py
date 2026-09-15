# expect: build
# source: Adafruit Learn CircuitPython Essentials servo example style
import time
import board
import pwmio
from adafruit_motor import servo

pwm = pwmio.PWMOut(board.D9, duty_cycle=0, frequency=50)
my_servo = servo.Servo(pwm)

while True:
    for angle in range(0, 180, 5):
        my_servo.angle = angle
        time.sleep(0.05)
    for angle in range(180, 0, -5):
        my_servo.angle = angle
        time.sleep(0.05)

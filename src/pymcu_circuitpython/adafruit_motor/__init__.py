# adafruit_motor for PyMCU
#
# The Adafruit driver package for motors and servos. Only `servo` is here so far, because
# the stepper and DC-motor halves want a motor driver board this layer has no HAL for.
#
#   from adafruit_motor import servo
#   import board, pwmio
#
#   pwm = pwmio.PWMOut(board.D9, frequency=50)
#   s = servo.Servo(pwm)
#   s.angle = 90

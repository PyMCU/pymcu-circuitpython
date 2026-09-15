# expect: build
# source: Regression corpus for passing a list of board pins to a driver class
import board
import digitalio


class LedBank:
    def __init__(self, pins):
        self.led0 = digitalio.DigitalInOut(pins[0])
        self.led1 = digitalio.DigitalInOut(pins[1])
        self.led2 = digitalio.DigitalInOut(pins[2])
        self.led0.direction = digitalio.Direction.OUTPUT
        self.led1.direction = digitalio.Direction.OUTPUT
        self.led2.direction = digitalio.Direction.OUTPUT

    def on(self):
        self.led0.value = True
        self.led1.value = True
        self.led2.value = True


bank = LedBank([board.D4, board.D5, board.D6])
bank.on()

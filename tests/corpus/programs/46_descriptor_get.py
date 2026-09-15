# expect: build
# source: Regression corpus for descriptor __get__ lookup
# note: used to be refused ("object has no attribute 'whoami'"); a class attribute defining
# __get__ is now recognized as a descriptor (PyMCU#268/#360). Verified in avr8sharp: prints
# 66 (0x42, Register.__get__'s return value), matching CPython.
class Register:
    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        return self.value


class Sensor:
    whoami = Register(0x42)

    def __init__(self):
        pass


sensor = Sensor()
print(sensor.whoami)

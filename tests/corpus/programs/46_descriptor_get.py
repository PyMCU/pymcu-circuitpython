# expect: refuse object has no attribute 'whoami'
# source: Regression corpus for descriptor __get__ lookup
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

# expect: build
# source: Regression corpus for user class kwargs passed through to a base class
class BaseSensor:
    def __init__(self, *, address=0x40, samples=1):
        self.address = address
        self.samples = samples


class Sensor(BaseSensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


sensor = Sensor(address=0x41, samples=4)
print(sensor.address, sensor.samples)

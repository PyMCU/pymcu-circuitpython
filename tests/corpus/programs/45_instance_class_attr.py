# expect: refuse object has no attribute 'ADDRESS'
# source: Regression corpus for reading a class attribute through an instance
class Device:
    ADDRESS = 0x68

    def __init__(self):
        pass


device = Device()
print(device.ADDRESS)

# expect: build
# source: Regression corpus for reading a class attribute through an instance
# note: used to be refused ("object has no attribute 'ADDRESS'"); a class attribute read
# through an instance now works (PyMCU#268/#360). Verified in avr8sharp: prints 104 (0x68),
# matching CPython.
class Device:
    ADDRESS = 0x68

    def __init__(self):
        pass


device = Device()
print(device.ADDRESS)

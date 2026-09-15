# expect: build
# source: Regression corpus for Optional annotations with None defaults


class Reading:
    def __init__(self, value: Optional[int] = None):
        self.value = value


reading = Reading()
if reading.value is None:
    print("missing")

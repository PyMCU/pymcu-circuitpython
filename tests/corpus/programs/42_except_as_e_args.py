# expect: build
# source: Regression corpus for except X as e and e.args[0]
try:
    raise RuntimeError("Timed out")
except RuntimeError as e:
    print(e.args[0])

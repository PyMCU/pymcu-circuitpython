# expect: build
# source: CircuitPython supervisor.ticks_ms docs wrap arithmetic style
import supervisor

start = supervisor.ticks_ms()

while True:
    now = supervisor.ticks_ms()
    if (now - start) & 0x1FFFFFFF > 1000:
        print(now)
        start = now

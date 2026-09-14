# CircuitPython-compatible keypad module for PyMCU
#
#   import board, keypad
#
#   buttons = [digitalio.DigitalInOut(board.D2),
#              digitalio.DigitalInOut(board.D3),
#              digitalio.DigitalInOut(board.D4)]
#   for b in buttons:
#       b.switch_to_input(pull=digitalio.Pull.UP)
#
#   keys = keypad.Keys(buttons, value_when_pressed=False)
#   event = keypad.Event()
#   while True:
#       if keys.events.get_into(event):
#           print(event.key_number, event.pressed)
#
# Buttons, and which one changed. No HAL half: a keypad is digitalio and bookkeeping, and
# the bookkeeping is the same on every architecture.
#
# WHAT IT TAKES. CircuitPython's Keys takes PINS and configures them itself. A list of pin
# names has no storage behind it here -- the names are compile-time values and the list
# cannot be indexed at run time (PyMCU#308) -- so this one takes a list of
# digitalio.DigitalInOut the caller has already made inputs, which a list of instances can
# be indexed. It is one more line in the program and the rest of the API is upstream's.
#
# WHEN THE SCAN HAPPENS. CircuitPython scans in the background on a tick and fills a queue.
# There is no background here, so the scan happens inside `events.get_into()`: the loop
# above reads the pins every time round, which is what it was already doing. What follows
# from that is the debouncing -- CircuitPython's `interval` is how often its background scan
# runs, and here it is how often the program calls get_into(), so the argument is refused
# rather than accepted and dropped.
#
# The queue holds no events of its own. A key's stored state is only updated when its change
# is reported, so a change that has not been read yet is still pending on the next call:
# that is what a queue is for, and it costs one bit a key instead of a buffer. `overflowed`
# is therefore always false, and it cannot be otherwise.

from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, inline, const


class Event:
    """Which key changed, and which way.

    CircuitPython's Event is immutable and carries a timestamp as well. This one is a
    buffer the queue writes into, because `get_into(event)` is the allocation-free half of
    the upstream API and the only half there is here.
    """

    @inline
    def __init__(self, key_number: uint8 = 0, pressed: uint8 = 0):
        self.key_number = key_number
        self.pressed = pressed

    @property
    def released(self) -> uint8:
        """1 when the key was released rather than pressed."""
        if self.pressed:
            return 0
        return 1


class _EventQueue:
    """The changes that have not been read yet.

    It holds nothing: a key's stored state moves only when its change is reported, so what
    is "in the queue" is exactly the set of keys whose pins disagree with what was last
    reported. One bit a key, and no buffer to overflow.

    The queue owns the pins rather than asking the Keys for them. A list of instances loses
    its iterability across one instance hop too many, and reaching through
    `self._keys._pins` was one: the for-in in here was refused as "not a compile-time
    iterable" while the identical loop one hop closer compiled.
    """

    @inline
    def __init__(self, pins, pressed_level: uint8):
        self._pins = pins
        self._pressed_level = pressed_level
        # One bit a key: what the pin said the last time a change was reported.
        self._last = 0

    # The three scans below walk the list with a for-in rather than indexing it. A list of
    # instances kept in a field has no run-time storage to index -- the compiler says so and
    # names the alternative -- and the for-in unrolls, so the key number is a constant in
    # each pass and the mask is a constant too.

    @inline
    def get_into(self, event) -> uint8:
        """Write the next change into `event` and return 1, or return 0 if there is none."""
        m: uint32 = 1
        k: uint8 = 0
        taken: uint8 = 0
        for p in self._pins:
            now: uint8 = 0
            if p.value == self._pressed_level:
                now = 1
            was: uint8 = 0
            if self._last & m:
                was = 1
            if now != was and taken == 0:
                if now:
                    self._last = self._last | m
                else:
                    self._last = self._last & (0xFFFFFFFF - m)
                event.key_number = k
                event.pressed = now
                taken = 1
            m = m + m
            k = k + 1
        return taken

    def get(self):
        """Not available: there is no heap to return an Event from."""
        raise CompileError(
            "keypad.EventQueue.get() returns a new Event object and there is no heap here to "
            "build one on. Make one Event of your own and call get_into(event), which is the "
            "same call upstream offers for exactly this reason: "
            "`event = keypad.Event()` once, then `if keys.events.get_into(event):` in the "
            "loop.")

    @inline
    def __len__(self) -> uint8:
        """How many keys have a change waiting to be read."""
        n: uint8 = 0
        m: uint32 = 1
        for p in self._pins:
            now: uint8 = 0
            if p.value == self._pressed_level:
                now = 1
            was: uint8 = 0
            if self._last & m:
                was = 1
            if now != was:
                n = n + 1
            m = m + m
        return n

    @inline
    def clear(self):
        """Forget every change that has not been read."""
        m: uint32 = 1
        for p in self._pins:
            if p.value == self._pressed_level:
                self._last = self._last | m
            else:
                self._last = self._last & (0xFFFFFFFF - m)
            m = m + m

    @property
    def overflowed(self) -> uint8:
        """Always 0: there is no buffer to overflow, because the pins themselves are the
        queue."""
        return 0


class Keys:
    """A set of buttons, each on its own pin.

    `pins` is a list of digitalio.DigitalInOut the caller has already switched to inputs,
    not a list of pin names: see the note at the top of this module.

    `value_when_pressed` is the level a pressed key puts on its pin: False for the usual
    button to ground with the pull-up on, True for one to the supply.

    Up to 32 keys, because the state of every key is kept as one bit of a 32-bit word, which
    is what lets the queue hold no events of its own.
    """

    @inline
    def __init__(self, pins, value_when_pressed: uint8 = 0,
                 interval: uint16 = 0, max_events: uint16 = 0):
        if interval != 0:
            raise CompileError(
                "keypad's `interval` is how often CircuitPython's background scan runs, and "
                "there is no background here: the scan happens inside events.get_into(), so "
                "how often it runs is how often your loop calls it. Drop the argument, and "
                "put the delay in your own loop if the keys need debouncing.")
        if max_events != 0:
            raise CompileError(
                "keypad's `max_events` sizes a queue of events, and this queue holds none: a "
                "key's state moves only when its change is reported, so what is waiting to "
                "be read is exactly the set of keys whose pins disagree with it. There is "
                "nothing to size and nothing to overflow. Drop the argument.")
        self._n = len(pins)
        if self._n > 32:
            raise CompileError(
                "a Keys holds up to 32 keys: the state of every one is a bit of a 32-bit "
                "word, which is what lets the queue keep no events of its own. Split the "
                "keypad into two Keys, or read the extra pins with digitalio directly.")
        self.events = _EventQueue(pins, value_when_pressed)

    @property
    def key_count(self) -> uint8:
        """How many keys this set has."""
        return self._n

    @inline
    def reset(self):
        """Take the pins as they are now, so nothing that happened before this counts."""
        self.events.clear()

    @inline
    def deinit(self):
        """Release the keys (the pins keep their direction and pull)."""
        pass

    @inline
    def __enter__(self):
        return self

    @inline
    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.deinit()

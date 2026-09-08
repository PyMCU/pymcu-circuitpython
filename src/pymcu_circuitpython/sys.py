# CircuitPython-compatible sys module for PyMCU
#
# Only `sys.implementation.name` is provided, because that is the whole of `sys`
# the CircuitPython library ecosystem reaches for at import time, and upstream
# calls `sys.implementation` "the recommended way to distinguish CircuitPython
# from other Python implementations".
#
# The rest of CircuitPython's sys -- argv, byteorder, maxsize, modules, path,
# platform, stderr, stdin, stdout, version, version_info, exit() -- is NOT here.
# Every one of them needs a runtime PyMCU does not have (a module table, a
# filesystem, a stream object), and a name that exists here but not on a board
# is the failure this layer exists to prevent.
#
# Why the value is "circuitpython": a program built against this layer is meant
# to be the same program that runs under CircuitPython, so the guards libraries
# write to tell the two apart have to fold the way they fold on a board. The
# alternative -- reporting some PyMCU-specific name -- would send every one of
# those guards down its CPython branch, importing `typing` and
# `circuitpython_typing`, which is the path a board never takes.
#
# The MicroPython flavor answers "micropython" from its own sys for the same
# reason: the identity follows the layer, because the layer is the claim.
#
# Usage:
#   import sys
#   if sys.implementation.name == "circuitpython":
#       ...


class _Implementation:
    """CircuitPython's sys.implementation.

    Only `name` is carried. Upstream also exposes `version`, `_machine`, `_mpy`
    and `_build`; those describe an interpreter build, and there is no
    interpreter here to describe.
    """

    def __init__(self):
        self.name = "circuitpython"


implementation = _Implementation()

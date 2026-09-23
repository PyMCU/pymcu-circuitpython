# CircuitPython-compatible sys module for PyMCU
#
# `sys.implementation.name`, `sys.platform`, `sys.version`, `sys.version_info`,
# `sys.byteorder` and `sys.maxsize` are provided. The first two are the `sys`
# reads the CircuitPython library ecosystem reaches for at import/branch time
# to tell interpreters apart (PyMCU docs/rfcs/0007 surveyed 20 vendored
# Adafruit libraries: `sys.implementation.name` / `sys.implementation.version[i]`
# are the shapes real libraries write). The other four are plain compile-time
# facts -- the pinned API surface and the target's own word size/endianness --
# that a module-level constant can state honestly.
#
# The rest of CircuitPython's sys -- argv, exit(), modules, path, stdin,
# stdout, stderr -- is NOT here. Every one of them describes a runtime PyMCU
# does not have (a module table, a filesystem search path, stream objects,
# command-line arguments), and a name that exists here but not on a board is
# the failure this layer exists to prevent.
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
# COMPILE-TIME CONSTANTS. `sys.implementation.name`, `sys.implementation.version`
# (and its indexing, `version[0]`) and `sys.platform` are resolved and
# substituted by the compiler at the point they are read, exactly the way
# `__CHIP__.arch` is (see pymcu.chips): the compiler folds the branch away
# before code generation. `sys.platform` below is a placeholder for IDEs and
# for `import pymcu_circuitpython.sys` under plain CPython (this layer's own
# parity suite) -- a compiled program never actually reads this file's global.
# The real per-board values are in docs/rfcs/0007 in the PyMCU repo:
#
#   sys.implementation.version is (10, 3, 1) on every board this layer
#   supports, because that is the CircuitPython API surface
#   pymcu-circuitpython's own parity suite is pinned against
#   (circuitpython-stubs>=10.3.1), not this package's own 0.x version. Bumping
#   it is a deliberate act tied to re-running the parity suite against a newer
#   stub package, not a side effect of a package release.
#
#   sys.platform is CircuitPython's own port string where one exists
#   ("RP2040" on the Pico, "RP2350" on the Pico 2 -- uppercase, and not the
#   same string as os.uname().sysname on the same port) and the plain chip
#   name where it does not (every AVR part, CH32V003 -- CircuitPython has
#   never had an upstream port for either): honest, since no such board is
#   really "RP2040" or "SAMD51" and a guard comparing against one of those
#   should take its generic (false) branch.
#
# `sys.version` reports "3.4.0; CircuitPython 10.3.1": the language level and
# the pinned API surface, both true facts. Upstream appends the firmware
# build date ("... on 2026-09-14") -- a fact about one specific firmware
# image that no layer can honestly claim, so it is left off rather than
# fabricated (the same call docs/rfcs/0007 made for os.uname().version).
#
# `sys.version_info` is (3, 4, 0), the Python language version CircuitPython
# 10.3.1 reports -- not the CircuitPython version (that is
# `sys.implementation.version`). It exists ONLY at the `sys.version_info[i]`
# read site: a tuple attribute has no honest module-level form under pymcuc,
# so the compiler folds the indexed read and the bare attribute (and
# `from sys import version_info`) refuses, the same contract
# `sys.implementation.version` holds.
#
# Usage:
#   import sys
#   if sys.implementation.name == "circuitpython":
#       ...
#   if sys.implementation.version[0] >= 7:
#       ...
#   if sys.platform == "RP2040":
#       ...


class _Implementation:
    """CircuitPython's sys.implementation.

    Only `name` is carried. `version` is deliberately absent from the OBJECT:
    it has no runtime form (the compiler substitutes (10, 3, 1) at the
    `sys.implementation.version[i]` fold, never here), so a tuple stored on
    this class could only be a placeholder -- and a program that binds the
    object (`impl = sys.implementation`) would then read the fake. Refusing
    the attribute is the layer's contract. Upstream also exposes `_machine`,
    `_mpy`, `_build` and (thread-enabled builds) `_thread`; those are private,
    undocumented build-introspection fields no surveyed library reads, and are
    left out for the same reason the rest of `sys` is (see module docstring
    above).
    """

    def __init__(self):
        self.name = "circuitpython"


implementation = _Implementation()

# Placeholder; the compiler substitutes the real per-board string (see module
# docstring). Illustrative default matches the Pico, the most common board
# this layer builds for.
platform = "RP2040"

# Honest constants -- the same on every board this layer supports.
# `version_info` is deliberately NOT a module attribute: a tuple global has no
# honest form under pymcuc, so the compiler folds `sys.version_info[i]` and the
# bare attribute refuses, exactly like `sys.implementation.version` (see the
# module docstring).
version = "3.4.0; CircuitPython 10.3.1"
byteorder = "little"
maxsize = 2147483647

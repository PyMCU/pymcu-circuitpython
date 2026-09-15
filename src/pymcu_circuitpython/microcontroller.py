# CircuitPython-compatible microcontroller module for PyMCU
#
# Mirrors CircuitPython's microcontroller module: microcontroller.cpu (a
# Processor instance), microcontroller.reset() and microcontroller.delay_us().
#
# Usage:
#   import microcontroller
#   hz   = microcontroller.cpu.frequency     # CPU frequency in Hz (compile-time)
#   degc = microcontroller.cpu.temperature   # die temperature in C (soft-float)
#   v    = microcontroller.cpu.voltage       # Vcc in volts (soft-float)
#   microcontroller.reset()                  # reset the MCU (watchdog)

from pymcu.chips import __CHIP__
from pymcu.exceptions import CompileError
from pymcu.types import uint8, uint16, uint32, inline, const, warning
if __CHIP__.arch == "avr":
    from pymcu.hal.adc import AnalogPin as _AnalogPin


class ResetReason:
    """Reason codes for the most recent reset (CircuitPython microcontroller.ResetReason).

    POWER_ON, BROWNOUT, RESET_PIN and WATCHDOG are produced on AVR from the
    MCUSR flag register. SOFTWARE, DEEP_SLEEP_ALARM and RESCUE_DEBUG are defined
    for API compatibility but never returned on this target (AVR software resets
    go through the watchdog and report WATCHDOG; there is no deep-sleep alarm or
    debug-rescue path here).
    """
    POWER_ON         = 0
    BROWNOUT         = 1
    SOFTWARE         = 2
    DEEP_SLEEP_ALARM = 3
    RESET_PIN        = 4
    WATCHDOG         = 5
    UNKNOWN          = 6
    RESCUE_DEBUG     = 7


class Processor:
    """Microcontroller CPU information (CircuitPython microcontroller.Processor)."""

    @property
    def frequency(self) -> const[uint32]:
        """CPU frequency in Hz (compile-time constant, as in CircuitPython)."""
        return __FREQ__

    @property
    @warning("microcontroller.cpu.temperature uses the software floating-point runtime and the uncalibrated on-chip sensor (approximate, +/-10 C).")
    def temperature(self) -> float:
        """Die temperature in degrees Celsius, read from the internal sensor.

        Uses the on-chip temperature sensor (ADC channel 8, 1.1V reference) and
        the datasheet transfer function. The reading is uncalibrated and only
        approximate (typical accuracy +/-10 C without per-chip calibration).
        Requires a chip with an internal temperature sensor (ATmega328P family).
        """
        adc = _AnalogPin("TEMP")
        adc.start()
        raw: uint16 = adc.read()
        # Datasheet (ATmega328P, table 28-1): ~1 LSB/C, offset ~324.31 at 0 C,
        # slope ~1.22 LSB/C. T = (raw - 324.31) / 1.22  (soft-float).
        return (raw - 324.31) / 1.22

    @property
    @warning("microcontroller.cpu.voltage uses the software floating-point runtime (bandgap-vs-AVcc measurement).")
    def voltage(self) -> float:
        """Supply voltage (Vcc) in volts.

        Measures the internal 1.1V bandgap reference against AVcc and back-
        computes Vcc = 1.1 * 1024 / ADCraw (soft-float). Requires a chip that
        exposes the bandgap channel (ATmega328P family).
        """
        adc = _AnalogPin("VBG")
        adc.start()
        raw: uint16 = adc.read()
        return 1.1 * 1024.0 / raw

    @property
    def uid(self):
        """Not available: this part has no unique serial this HAL will vouch for.

        It used to return a tuple of eight zeros, which reads as a real identifier that
        happens to be zero -- two boards would have compared equal and a program keying
        anything on it would have keyed on nothing.

        The ATmega parts do carry a signature row with numbers that differ between dies, but
        Atmel documents neither its layout nor its uniqueness, and reading it needs the
        boot-loader instruction path. An identifier a program can rely on is one the program
        writes: put a random value in microcontroller.nvm the first time a board boots and
        read it back after that.
        """
        raise CompileError(
            "this part has no unique serial number this HAL will vouch for. The ATmega "
            "signature row holds numbers that differ between dies, but their layout and "
            "their uniqueness are undocumented, so reading them would be a guess presented "
            "as an identity. Write your own: store a random value in microcontroller.nvm "
            "the first time a board boots and read it back after that. It used to return "
            "eight zeros, which two boards would have agreed on.")

    @property
    @warning("microcontroller.cpu.reset_reason reads MCUSR live; PyMCU does not snapshot/clear it at boot, so flags can accumulate across resets (best-effort). Clear MCUSR early in your program for a single-event reading.")
    def reset_reason(self) -> uint8:
        """Reason for the most recent reset, as a ResetReason value.

        Reads the AVR MCUSR flag register (DATA 0x54 / I/O 0x34) directly.
        Specific events are checked before POWER_ON because, without a boot-time
        clear, the power-on flag lingers across later resets; checking WATCHDOG/
        BROWNOUT/RESET_PIN first yields the more useful answer in that case.
        """
        from pymcu.types import ptr
        MCUSR: ptr[uint8] = ptr(0x54)
        if MCUSR[3]:        # WDRF  -- watchdog system reset
            return ResetReason.WATCHDOG
        if MCUSR[2]:        # BORF  -- brown-out reset
            return ResetReason.BROWNOUT
        if MCUSR[1]:        # EXTRF -- external reset pin
            return ResetReason.RESET_PIN
        if MCUSR[0]:        # PORF  -- power-on reset
            return ResetReason.POWER_ON
        return ResetReason.UNKNOWN


# CircuitPython exposes the processor as `microcontroller.cpu`.
cpu = Processor()


class _Cpus:
    """The processors this part has, as a sequence.

    CircuitPython has `microcontroller.cpus`, a sequence of Processor. This part has one
    core, so `len(cpus)` is 1.

    Indexing it is refused. An object handed back from __getitem__ loses what it is on the
    way out -- `cpus[0].frequency` comes back as "unknown member access: frequency" -- so
    returning the Processor would compile into something a program cannot use. The refusal
    names `microcontroller.cpu`, which is upstream's own name for the current core and is
    the same object.
    """

    @inline
    def __len__(self) -> uint8:
        return 1

    def __getitem__(self, index: uint8):
        raise CompileError(
            "microcontroller.cpus cannot be indexed here: a processor handed back from an "
            "index loses its type on the way out, so cpus[0].frequency would not compile "
            "even though cpus[0] did. Use microcontroller.cpu, which is upstream's name for "
            "the current core and is the same object. len(cpus) works and is 1 on this part.")


cpus = _Cpus()


@inline
def reset():
    """Reset the microcontroller immediately.

    Implemented via the watchdog timer with the shortest timeout (~16 ms): the
    watchdog is armed in reset mode and the CPU spins until it fires, which
    restarts execution from the reset vector -- the bare-metal equivalent of
    CircuitPython's microcontroller.reset().
    """
    from pymcu.hal.watchdog import Watchdog as _Watchdog
    wd = _Watchdog(16)
    wd.enable()
    while True:
        pass


@inline
def delay_us(delay: uint32):
    """Busy-wait for the given number of microseconds (CircuitPython parity)."""
    from pymcu.time import delay_us as _delay_us
    _delay_us(delay)


class Pin:
    """A pin, as CircuitPython's microcontroller.Pin.

    Empty on purpose, and it stays empty. In CircuitPython `board.D2` IS one of these and
    carries the port and bit; here a board pin is the name string the HAL's tables are keyed
    on, which is what lets every pin decision fold at compile time. The class is here so that
    code which only mentions the type -- an annotation, an isinstance that never runs --
    still resolves.
    """
    pass


# ---------------------------------------------------------------------------
# microcontroller.nvm -- byte-addressable non-volatile memory (EEPROM-backed)
# ---------------------------------------------------------------------------

class _NVM:
    """Persistent byte storage (CircuitPython microcontroller.nvm).

    Backed by the on-chip EEPROM: nvm[i] reads a byte, nvm[i] = v writes one,
    and len(nvm) is the EEPROM size in bytes. Writes survive resets and power
    cycles. Every accessor expands inline to the EEPROM HAL (zero overhead).

    Deviations from CircuitPython:
      - Slice access (nvm[a:b]) needs a heap-allocated bytearray and is not
        available on bare metal; index one byte at a time in a loop instead.
      - len(nvm) is 1024, the ATmega328P's EEPROM, on every chip. The part's real size
        is EEPROM_SIZE in pymcu.hal.eeprom; this cannot ask for it, because a slice of nvm
        needs the length folded to a literal here (PyMCU#329).
    """

    # The HAL's constant, not a call: a slice of nvm needs this length to fold to a literal,
    # and even one method hop into the HAL is enough to stop it -- nvm[0:4] failed with
    # "slice indexing is only supported on named fixed-size arrays".
    # A LITERAL, and it has to be. A slice of nvm needs this length folded to one, and
    # nothing else reaches it: a method hop into the HAL, and a module-level constant
    # imported from the HAL, both make nvm[0:4] fail with "slice indexing is only supported
    # on named fixed-size arrays" (PyMCU#329). The part's real size is EEPROM_SIZE in
    # pymcu.hal.eeprom, which is where the fact belongs; this number is the ATmega328P's and
    # is wrong on an ATtiny85 (512) and an ATmega2560 (4096), which is the half of #16 that
    # is still open.
    @inline
    def __len__(self) -> uint16:
        return 1024

    @inline
    def __getitem__(self, index: uint16) -> uint8:
        from pymcu.hal.eeprom import EEPROM as _EEPROM
        return _EEPROM().read(index)

    @inline
    def __setitem__(self, index: uint16, value: uint8):
        from pymcu.hal.eeprom import EEPROM as _EEPROM
        _EEPROM().write(index, value)


# CircuitPython exposes persistent storage as microcontroller.nvm.
nvm = _NVM()


# ---------------------------------------------------------------------------
# microcontroller.watchdog -- hardware watchdog timer
#
# WatchDogTimer lives in watchdog.py, not here: this module used to define it and
# watchdog.py imported it back, a cycle the compiler refuses (it needs a DAG of module
# dependencies, unlike CPython's tolerance for partial modules across a two-way import).
# ---------------------------------------------------------------------------

from watchdog import WatchDogTimer

# CircuitPython exposes the watchdog as microcontroller.watchdog.
watchdog = WatchDogTimer()


# ---------------------------------------------------------------------------
# Interrupt control
#
# There was no reason these were missing: pymcu.hal.irq has implemented both
# since well before this layer existed. Nothing in the compiler or the part was
# in the way; nobody had wired them through.
#
# Delegating rather than writing asm("sei") here, because the HAL is
# arch-dispatched (AVR SEI/CLI, Cortex-M CPSIE/CPSID, PIC GIE, RISC-V
# mstatus.MIE) and this layer also serves RP2040. Hard-coding AVR would work
# today and break the first time someone builds for a Pico.
#
# Verified in the listing: a program calling both emits one SEI and one CLI,
# confirmed against avr-objdump on the ELF as well as the generated .asm.
# ---------------------------------------------------------------------------

from pymcu.hal.irq import enable_interrupts as _hal_enable
from pymcu.hal.irq import disable_interrupts as _hal_disable


@inline
def disable_interrupts():
    """Disable interrupts globally (CircuitPython microcontroller.disable_interrupts).

    Does NOT nest, matching neither more nor less than the hardware does: two
    disables followed by one enable leaves interrupts ON. Upstream counts
    nesting on some ports; this one cannot, so pair them one to one.
    """
    _hal_disable()


@inline
def enable_interrupts():
    """Enable interrupts globally. See disable_interrupts() for the nesting note."""
    _hal_enable()


# ---------------------------------------------------------------------------
# microcontroller.cpus
#
# Upstream is a sequence of Processor objects. This part has one core, and cpus is a
# sequence of one so that cpus[0] and len(cpus) compile, which is how portable code reaches
# the first core. `cpu` is upstream's name for the current core and is the shorter spelling.
# ---------------------------------------------------------------------------

# cpus is _Cpus() above: a sequence of one, so that microcontroller.cpus[0] compiles.
# WatchDogMode lives in the `watchdog` module upstream, not here. Re-exported
# for the code that already imports it from microcontroller; prefer
# `from watchdog import WatchDogMode`, which is what a CircuitPython program
# on a board will be using.
from watchdog import WatchDogMode

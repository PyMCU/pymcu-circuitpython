"""Cross-module smoke: the common CircuitPython idioms used together."""
from unittest.mock import MagicMock, patch

from pymcu_circuitpython.digitalio import DigitalInOut, Direction, Pull
from pymcu_circuitpython.busio import UART
from pymcu_circuitpython.analogio import AnalogIn
from pymcu_circuitpython.pwmio import PWMOut
from pymcu_circuitpython import microcontroller, alarm, time
from pymcu_circuitpython.microcontroller import WatchDogMode, ResetReason


def test_gpio_uart_adc_pwm_together():
    led = DigitalInOut("PB5")
    led.direction = Direction.OUTPUT
    led.value = True

    btn = DigitalInOut("PD2")
    btn.switch_to_input(pull=Pull.UP)
    _ = btn.value

    uart = UART(None, None, baudrate=9600)
    uart.write(b"hi")

    adc = AnalogIn("PC0")
    pwm = PWMOut("PD6", duty_cycle=0)
    pwm.duty_cycle = adc.value & 0xFFFF


def test_reboot_counter_with_nvm_and_watchdog():
    """A realistic boot idiom: persist a reboot counter in NVM, classify the
    reset cause, then arm + feed the watchdog -- exercising nvm, reset_reason
    and watchdog together."""
    import pymcu.hal.watchdog as _wd

    # Persistent reboot counter in EEPROM-backed NVM.
    before = microcontroller.nvm[0]
    microcontroller.nvm[0] = (before + 1) & 0xFF
    assert microcontroller.nvm[0] == (before + 1) & 0xFF
    assert len(microcontroller.nvm) == 1024

    # reset_reason reads MCUSR on-target; on host it stays a descriptor, and the
    # ResetReason codes are usable in comparisons either way.
    assert isinstance(type(microcontroller.cpu).reset_reason, property)
    assert ResetReason.WATCHDOG != ResetReason.POWER_ON

    # Arm the watchdog from a runtime timeout, then feed it once.
    fake = MagicMock()
    with patch.object(_wd, "Watchdog", MagicMock(return_value=fake)):
        microcontroller.watchdog.timeout = 4          # seconds
        microcontroller.watchdog.mode = WatchDogMode.RESET
        microcontroller.watchdog.feed()
        fake.arm_ms.assert_called_once_with(4000)     # armed with runtime ms
        fake.feed.assert_called_once()


def test_alarm_sleep_then_reset_idiom():
    """Wake on a TimeAlarm via both the light- and deep-sleep entry points,
    then trigger a software reset path (watchdog) -- alarm + microcontroller."""
    ta = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 1)
    assert alarm.light_sleep_until_alarms(ta) == 0
    assert alarm.exit_and_deep_sleep_until_alarms(ta) == 0

    # microcontroller.reset() arms the watchdog and spins; confirm it reaches
    # the watchdog (patched to break the infinite loop).
    import pymcu.hal.watchdog as _wd

    class _Boom(Exception):
        pass

    class _WD:
        def __init__(self, timeout_ms=500):
            pass

        def enable(self):
            raise _Boom

    with patch.object(_wd, "Watchdog", _WD):
        try:
            microcontroller.reset()
        except _Boom:
            pass
        else:
            raise AssertionError("reset() did not arm the watchdog")

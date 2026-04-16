# DHT11 temperature & humidity driver (CircuitPython style)
#
# Pass the DATA pin as a board constant:
#   sensor = DHT11(board.D2)
#
# Call sensor.measure() to read; then check sensor.failed before using:
#   sensor.humidity     -- integer % RH (20-90)
#   sensor.temperature  -- integer degrees Celsius (0-50)
#   sensor.failed       -- True if the read failed or checksum mismatch
#
# Wiring:
#   DHT11 DATA -> pin passed in (e.g. D2), with 4.7 kohm pull-up to +5 V
#   DHT11 VCC  -> +5 V
#   DHT11 GND  -> GND
#
# Protocol (single-wire, 40-bit):
#   1. MCU pulls low >= 18 ms  (start signal)
#   2. MCU releases, sensor pulls low ~80 us then high ~80 us (ACK)
#   3. 40 bits: each bit starts with ~50 us LOW; HIGH duration decides value:
#      ~28 us = 0,  ~70 us = 1  (threshold: 40 us)
#   4. Checksum = lower 8 bits of sum of the first 4 bytes

from pymcu.types import uint8, uint16, inline
from pymcu.hal.gpio import Pin as _Pin
from pymcu.time import delay_ms, delay_us


class DHT11:
    @inline
    def __init__(self, pin_name):
        self._pin       = _Pin(pin_name, _Pin.IN)
        self.failed     = False
        self.humidity   = 0
        self.temperature = 0

    @inline
    def measure(self):
        # Start signal: hold low >= 18 ms, then release
        self._pin.mode(_Pin.OUT)
        self._pin.low()
        delay_ms(18)
        self._pin.high()
        delay_us(30)
        self._pin.mode(_Pin.IN)

        # ACK: sensor pulls low ~80 us, then high ~80 us
        ack_lo: uint16 = self._pin.pulse_in(0, 1000)
        if ack_lo == 0:
            self.failed = True
            return

        ack_hi: uint16 = self._pin.pulse_in(1, 1000)
        if ack_hi == 0:
            self.failed = True
            return

        # Read five bytes: hum_int, hum_dec, temp_int, temp_dec, checksum
        hum_int:  uint8 = self._read_byte()
        hum_dec:  uint8 = self._read_byte()
        temp_int: uint8 = self._read_byte()
        temp_dec: uint8 = self._read_byte()
        checksum: uint8 = self._read_byte()

        # Verify checksum (sum of first 4 bytes, low 8 bits)
        expected: uint8 = (hum_int + hum_dec + temp_int + temp_dec) & 0xFF
        if checksum != expected:
            self.failed = True
            return

        self.failed      = False
        self.humidity    = hum_int
        self.temperature = temp_int

    @inline
    def _read_byte(self) -> uint8:
        # Each bit: ~50 us LOW preamble (ignored), then HIGH duration decides value.
        # Threshold 40 us: shorter = 0, longer = 1.
        result: uint8 = 0
        i: uint8 = 0
        while i < 8:
            duration: uint16 = self._pin.pulse_in(1, 1000)
            result = result << 1
            if duration > 40:
                result = result | 1
            i = i + 1
        return result

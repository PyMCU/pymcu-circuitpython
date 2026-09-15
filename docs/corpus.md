# Corpus

The corpus compiles each program with `/Users/begeistert/PycharmProjects/cp-hcsr04/.venv/bin/pymcu`
unless `PYMCU_BIN` overrides it. The template targets `arduino_uno`.

Totals from the first recorded run: 29 build, 20 refused.

## Refused Today

| Program | Diagnostic |
| --- | --- |
| 06_i2c_scan.py | list comprehension is only supported where it fills a fixed array whose length is a compile-time constant |
| 08_spi_write.py | bytearray() is a Python builtin that PyMCU does not provide |
| 10_uart_echo_read.py | busio.UART.read() returns a bytes object |
| 15_keypad_keys.py | unknown keyword argument 'pull' in call to constructor of 'Keys' |
| 17_watchdog.py | call to undefined function 'w_feed' |
| 18_alarm_time.py | name 'alarm0' is not defined |
| 24_i2c_register_read.py | bytearray() is a Python builtin that PyMCU does not provide |
| 25_bitbang_i2c.py | bytearray() is a Python builtin that PyMCU does not provide |
| 26_bitbang_spi.py | bytearray() is a Python builtin that PyMCU does not provide |
| 28_pulseout_ir.py | Bit index must be constant for reading |
| 32_pwm_variable_frequency.py | a PWM running at an exact frequency cannot be retuned at run time |
| 33_alarm_multiple.py | name 'alarm0' is not defined |
| 36_analogout_refuse.py | this chip has no digital-to-analog converter |
| 37_uart_readline_refuse.py | busio.UART.readline() returns a bytes object |
| 38_keypad_event_get_refuse.py | unknown keyword argument 'pull' in call to constructor of 'Keys' |
| 39_rotary_diff_ports_refuse.py | an encoder's two lines have to be on the same port |
| 40_pulseout_wrong_pin_refuse.py | a pulse train's carrier comes out of OC2B |
| 45_instance_class_attr.py | object has no attribute 'ADDRESS' |
| 46_descriptor_get.py | object has no attribute 'whoami' |
| 48_class_field_dict_lists.py | array index must be an integer |

## Five Largest

| Program | Flash bytes |
| --- | ---: |
| 13_hcsr04_pulseio.py | 3372 |
| 22_analog_voltage.py | 2884 |
| 35_cpu_temperature.py | 2750 |
| 14_rotary_encoder.py | 1844 |
| 16_time_monotonic_loop.py | 1378 |

## Full Table

| Program | Expectation | Outcome | Bytes | Diagnostic |
| --- | --- | --- | ---: | --- |
| 01_blink.py | build | build | 152 |  |
| 02_button_pullup.py | build | build | 182 |  |
| 03_pwm_fade.py | build | build | 554 |  |
| 04_servo_sweep.py | build | build | 1208 |  |
| 05_analog_read_serial.py | build | build | 650 |  |
| 06_i2c_scan.py | refuse list comprehension is only supported | refuse |  | list comprehension is only supported where it fills a fixed array whose length is a compile-time constant |
| 07_i2c_probe_loop.py | build | build | 614 |  |
| 08_spi_write.py | refuse bytearray() is a Python builtin that PyMCU does not provide | refuse |  | bytearray() is a Python builtin that PyMCU does not provide |
| 09_uart_echo_readinto.py | build | build | 832 |  |
| 10_uart_echo_read.py | refuse busio.UART.read() returns a bytes object | refuse |  | busio.UART.read() returns a bytes object |
| 11_neopixel_write_raw.py | build | build | 312 |  |
| 12_neopixel_fill_tuple.py | build | build | 1130 |  |
| 13_hcsr04_pulseio.py | build | build | 3372 |  |
| 14_rotary_encoder.py | build | build | 1844 |  |
| 15_keypad_keys.py | refuse unknown keyword argument 'pull' | refuse |  | unknown keyword argument 'pull' in call to constructor of 'Keys' |
| 16_time_monotonic_loop.py | build | build | 1378 |  |
| 17_watchdog.py | refuse call to undefined function 'w_feed' | refuse |  | call to undefined function 'w_feed' |
| 18_alarm_time.py | refuse name 'alarm0' is not defined | refuse |  | name 'alarm0' is not defined |
| 19_alarm_pin.py | build | build | 418 |  |
| 20_supervisor_ticks_ms.py | build | build | 1376 |  |
| 21_digitalio_context.py | build | build | 174 |  |
| 22_analog_voltage.py | build | build | 2884 |  |
| 23_spi_write_readinto.py | build | build | 440 |  |
| 24_i2c_register_read.py | refuse bytearray() is a Python builtin that PyMCU does not provide | refuse |  | bytearray() is a Python builtin that PyMCU does not provide |
| 25_bitbang_i2c.py | refuse bytearray() is a Python builtin that PyMCU does not provide | refuse |  | bytearray() is a Python builtin that PyMCU does not provide |
| 26_bitbang_spi.py | refuse bytearray() is a Python builtin that PyMCU does not provide | refuse |  | bytearray() is a Python builtin that PyMCU does not provide |
| 27_pulsein_ir.py | build | build | 1062 |  |
| 28_pulseout_ir.py | refuse Bit index must be constant for reading | refuse |  | Bit index must be constant for reading |
| 29_countio_edges.py | build | build | 1180 |  |
| 30_rainbowio_neopixel_write.py | build | build | 1172 |  |
| 31_uart_7e1.py | build | build | 428 |  |
| 32_pwm_variable_frequency.py | refuse a PWM running at an exact frequency cannot be retuned at run time | refuse |  | a PWM running at an exact frequency cannot be retuned at run time |
| 33_alarm_multiple.py | refuse name 'alarm0' is not defined | refuse |  | name 'alarm0' is not defined |
| 34_nvm_counter.py | build | build | 580 |  |
| 35_cpu_temperature.py | build | build | 2750 |  |
| 36_analogout_refuse.py | refuse this chip has no digital-to-analog converter | refuse |  | this chip has no digital-to-analog converter |
| 37_uart_readline_refuse.py | refuse busio.UART.readline() returns a bytes object | refuse |  | busio.UART.readline() returns a bytes object |
| 38_keypad_event_get_refuse.py | refuse unknown keyword argument 'pull' | refuse |  | unknown keyword argument 'pull' in call to constructor of 'Keys' |
| 39_rotary_diff_ports_refuse.py | refuse an encoder's two lines have to be on the same port | refuse |  | an encoder's two lines have to be on the same port |
| 40_pulseout_wrong_pin_refuse.py | refuse a pulse train's carrier comes out of OC2B | refuse |  | a pulse train's carrier comes out of OC2B |
| 41_kwargs_base_class.py | build | build | 356 |  |
| 42_except_as_e_args.py | build | build | 336 |  |
| 43_optional_annotation_none.py | build | build | 180 |  |
| 44_module_float_constant.py | build | build | 1038 |  |
| 45_instance_class_attr.py | refuse object has no attribute 'ADDRESS' | refuse |  | object has no attribute 'ADDRESS' |
| 46_descriptor_get.py | refuse object has no attribute 'whoami' | refuse |  | object has no attribute 'whoami' |
| 47_print_tuple.py | build | build | 366 |  |
| 48_class_field_dict_lists.py | refuse array index must be an integer | refuse |  | array index must be an integer |
| 49_list_pins_driver.py | build | build | 140 |  |

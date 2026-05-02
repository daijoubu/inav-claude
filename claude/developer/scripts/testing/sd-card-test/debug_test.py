#!/usr/bin/env python3
import time
from sd_card_test.fc_control import FCControl
from sd_card_test.msc_handler import MSCHandler
from sd_card_test.tests import TestSuite

fc = FCControl('/dev/ttyACM0')
if not fc.connect():
    print('Failed to connect')
    exit(1)

print('Connected, checking SD...')
sd = fc.get_sd_card_status()
print(f'SD: {sd.state_name if sd else "None"}')

print('\nRunning Test 1...')
msc = MSCHandler('/dev/ttyACM0')
suite = TestSuite(fc, msc, verbose=True)
result = suite.run_test(1)
print(f'Test 1: {"PASS" if result.passed else "FAIL"} - {result.error}')

print('\nRunning Test 2...')
result = suite.run_test(2, duration_sec=10)
print(f'Test 2: {"PASS" if result.passed else "FAIL"} - {result.error}')

fc.disconnect()

#!/usr/bin/env python3
"""
SD Card Test Automation for MATEKF765SE
=======================================

Automated tests for validating SD card reliability before/after HAL update.
Uses MSP protocol to communicate with flight controller.

This is a backward-compatible wrapper. The actual implementation is in sd_card_test/.

Tests:
- Test 1: SD Card Detection
- Test 2: Write Speed
- Test 3: Continuous Logging
- Test 4: High-Frequency Logging
- Test 6: Arm/Disarm Cycles
- Test 8: GPS Fix + Arm
- Test 9: Extended Endurance
- Test 10: DMA Contention
- Test 11: Blocking Measurement

Usage:
    python sd_card_test.py /dev/ttyACM0
    python sd_card_test.py /dev/ttyACM0 --test 1,2,3

Requirements:
    - Python 3.9+
    - mspapi2 library
    - Flight controller connected via USB/serial
"""

import sys
from sd_card_test.main import main

if __name__ == "__main__":
    main()

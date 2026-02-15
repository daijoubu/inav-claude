#!/usr/bin/env python3
"""
Test script for MSP2_INAV_MOTOR_LOCATE command.

This script tests the firmware's motor locate functionality by sending
MSP2_INAV_MOTOR_LOCATE commands directly to the flight controller.

The motor locate feature:
- Makes individual motors beep (DShot beacon commands)
- Does a brief jerk then 4 ascending beeps over ~2 seconds
- Helps users identify which motor number corresponds to which physical position
- Only works when disarmed with DShot protocol

Usage:
    ./test_motor_locate.py /dev/ttyACM0
    ./test_motor_locate.py /dev/ttyACM0 --motor 0
    ./test_motor_locate.py localhost:5760
    ./test_motor_locate.py --all-motors
    ./test_motor_locate.py --test-safety

Requirements:
    - mspapi2 library (pip install -e /path/to/mspapi2)
    - Flight controller with DShot ESCs
    - Props OFF for safety!
    - Flight controller DISARMED
"""

import argparse
import sys
import time
import struct
from typing import Optional

# Try to import mspapi2
try:
    from mspapi2 import MSPApi
    from mspapi2.msp_serial import MSPSerial
except ImportError:
    print("ERROR: mspapi2 not found!")
    print("Install with: pip install -e /path/to/mspapi2")
    print("(mspapi2 is located at: ~/Documents/planes/inavflight/mspapi2)")
    sys.exit(1)

# MSP command codes
MSP2_INAV_MOTOR_LOCATE = 0x2042

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_success(msg):
    """Print success message in green."""
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    """Print error message in red."""
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    """Print info message in blue."""
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_header(msg):
    """Print section header."""
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")


def connect_to_fc(connection_string: str) -> MSPApi:
    """
    Connect to flight controller via serial port or TCP.

    Returns:
        MSPApi instance (already opened)

    Raises:
        Exception on connection failure
    """
    print_info(f"Connecting to: {connection_string}")

    # Parse connection string
    if ':' in connection_string:
        # TCP connection
        api = MSPApi(tcp_endpoint=connection_string)
    else:
        # Serial connection
        api = MSPApi(port=connection_string, baudrate=115200)

    try:
        api.open()
        print_success("Connected to flight controller")
        return api
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        print_warning("Check:")
        print("  - Is the FC plugged in?")
        print("  - Is the configurator closed?")
        print("  - Do you have permission to access the serial port?")
        print("  - If running in sandbox: retry with dangerouslyDisableSandbox: true")
        raise


def verify_fc_responding(api: MSPApi) -> bool:
    """
    Verify the FC is responding to MSP commands.

    Returns:
        True if FC responds, False otherwise
    """
    print_info("Verifying FC is responding...")

    try:
        info, version = api.get_api_version()
        print_success(f"FC responding: API {version['apiVersionMajor']}.{version['apiVersionMinor']}")
        return True
    except Exception as e:
        print_error(f"FC not responding: {e}")
        print_warning("The test cannot run reliably.")
        return False


def check_armed_state(api: MSPApi) -> bool:
    """
    Check if FC is armed.

    Returns:
        True if armed, False if disarmed
    """
    try:
        # Get status to check arming flags
        info, status = api.get_status()

        # Check if ARMED flag is set (bit 0)
        is_armed = bool(status['armingFlags'] & 0x01)

        if is_armed:
            print_error("FC is ARMED!")
        else:
            print_success("FC is disarmed")

        return is_armed
    except Exception as e:
        print_error(f"Failed to check armed state: {e}")
        return True  # Assume armed for safety


def send_motor_locate(api: MSPApi, motor_index: int) -> bool:
    """
    Send MSP2_INAV_MOTOR_LOCATE command.

    Args:
        motor_index: Motor index (0-based) or 255 to stop all

    Returns:
        True if command sent successfully
    """
    try:
        # Pack payload: 1 byte motor index
        payload = struct.pack('<B', motor_index)

        # Send raw MSP command
        response = api.transport.request(MSP2_INAV_MOTOR_LOCATE, payload)

        if motor_index == 255:
            print_success("Sent STOP command")
        else:
            print_success(f"Sent locate command for motor {motor_index}")

        return True

    except Exception as e:
        print_error(f"Failed to send command: {e}")
        return False


def test_single_motor(api: MSPApi, motor_index: int, duration: float = 3.0):
    """
    Test a single motor locate sequence.

    Args:
        motor_index: Motor index to test (0-based)
        duration: How long to wait for beeps (seconds)
    """
    print_header(f"Testing Motor {motor_index}")

    # Check armed state before each test
    if check_armed_state(api):
        print_error("Cannot locate motors while armed!")
        return False

    # Send locate command
    if not send_motor_locate(api, motor_index):
        return False

    # Wait for sequence to complete
    print_info(f"Listening for motor {motor_index} beeps (~2 second sequence)...")
    print("Expected pattern: 100ms jerk, then 4 ascending beeps")
    time.sleep(duration)

    # Stop locate (cleanup)
    send_motor_locate(api, 255)

    return True


def test_all_motors(api: MSPApi, num_motors: int = 4):
    """
    Test all motors in sequence.

    Args:
        num_motors: Number of motors to test
    """
    print_header(f"Testing All {num_motors} Motors")

    for i in range(num_motors):
        print(f"\n{BOLD}--- Motor {i} ---{RESET}")

        if not test_single_motor(api, i, duration=2.5):
            print_error(f"Test failed for motor {i}")
            continue

        # Pause between motors
        if i < num_motors - 1:
            print_info("Pausing before next motor...")
            time.sleep(1.0)

    print_header("All Motors Test Complete")


def test_safety_checks(api: MSPApi):
    """
    Test that safety checks work correctly.
    """
    print_header("Testing Safety Checks")

    # Check armed state
    print_info("Checking armed state check...")
    if check_armed_state(api):
        print_warning("FC is armed - motor locate should be blocked by firmware")
        print("Attempting to send locate command (should fail)...")
        send_motor_locate(api, 0)
        time.sleep(1)
        print_info("If you heard beeps, the safety check is BROKEN!")
    else:
        print_success("Safety check: FC must be disarmed ✓")

    # Test stop command
    print_info("\nTesting STOP command (motor_index=255)...")
    if send_motor_locate(api, 255):
        print_success("STOP command works ✓")


def main():
    parser = argparse.ArgumentParser(
        description="Test MSP2_INAV_MOTOR_LOCATE command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /dev/ttyACM0              # Test motor 0 on serial port
  %(prog)s localhost:5760            # Test motor 0 on SITL
  %(prog)s /dev/ttyACM0 --motor 2    # Test specific motor
  %(prog)s /dev/ttyACM0 --all-motors # Test all motors sequentially
  %(prog)s /dev/ttyACM0 --test-safety # Test safety checks

SAFETY WARNINGS:
  - REMOVE PROPELLERS before testing!
  - Ensure FC is DISARMED
  - Only works with DShot protocol
  - Motors will jerk briefly (12%% throttle for 100ms)
        """
    )

    parser.add_argument(
        'connection',
        help='Serial port (e.g., /dev/ttyACM0) or TCP endpoint (e.g., localhost:5760)'
    )
    parser.add_argument(
        '--motor',
        type=int,
        default=None,
        help='Motor index to test (0-based). Default: 0'
    )
    parser.add_argument(
        '--all-motors',
        action='store_true',
        help='Test all motors in sequence'
    )
    parser.add_argument(
        '--num-motors',
        type=int,
        default=4,
        help='Number of motors (default: 4)'
    )
    parser.add_argument(
        '--test-safety',
        action='store_true',
        help='Test safety checks instead of motor locate'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=3.0,
        help='How long to wait for beeps (seconds, default: 3.0)'
    )

    args = parser.parse_args()

    # Safety banner
    print_header("MSP2_INAV_MOTOR_LOCATE Test Script")
    print(f"{RED}{BOLD}⚠ SAFETY WARNING ⚠{RESET}")
    print(f"{RED}REMOVE PROPELLERS BEFORE TESTING!{RESET}")
    print("Motors will jerk briefly during the test.")
    print()

    try:
        # Connect to FC
        api = connect_to_fc(args.connection)

        # Verify FC is responding
        if not verify_fc_responding(api):
            return 1

        # Get FC info
        info, variant = api.get_fc_variant()
        print_info(f"FC Variant: {variant['fcVariantIdentifier']}")

        # Check armed state
        print()
        if check_armed_state(api):
            print_error("FC is ARMED - aborting test!")
            print("Motor locate only works when disarmed.")
            return 1

        # Run requested test
        if args.test_safety:
            test_safety_checks(api)
        elif args.all_motors:
            test_all_motors(api, args.num_motors)
        else:
            motor_index = args.motor if args.motor is not None else 0
            test_single_motor(api, motor_index, args.duration)

        # Cleanup: ensure motors stopped
        print()
        print_info("Sending final STOP command...")
        send_motor_locate(api, 255)

        print_header("Test Complete")
        print("Check results:")
        print("  ✓ Did you hear/feel the motor?")
        print("  ✓ Was it the correct motor number?")
        print("  ✓ Did the sequence last ~2 seconds?")
        print()

        api.close()
        return 0

    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        return 130
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

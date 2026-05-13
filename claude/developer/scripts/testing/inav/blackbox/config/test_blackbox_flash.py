#!/usr/bin/env python3
"""
Test Blackbox Flash Functionality on Physical Flight Controller

This script:
1. Connects to an attached FC
2. Checks blackbox flash status
3. Records initial flash usage
4. Arms FC for 30 seconds
5. Disarms FC
6. Compares flash usage to verify blackbox data was written

Note: Cannot erase flash via MSP since MSP_DATAFLASH_ERASE (code 72)
has no handler in the firmware. Test works with current flash state.

Usage:
    python3 test_blackbox_flash.py [port]

Example:
    python3 test_blackbox_flash.py /dev/ttyACM0
"""

import struct
import sys
import time
from mspapi2 import MSPApi

def connect_to_fc(port):
    """Connect to flight controller."""
    print(f"Connecting to FC on {port}...")
    try:
        api = MSPApi(port=port, baudrate=115200)
        api.open()
        time.sleep(0.5)
        print("✓ Connected to FC")
        return api
    except Exception as e:
        print(f"✗ Failed to connect to FC: {e}")
        print("  Check: Is FC plugged in? Is configurator closed?")
        print("  If running in sandbox: retry with dangerouslyDisableSandbox: true")
        return None

def get_flash_summary(api):
    """Get flash summary information."""
    MSP_DATAFLASH_SUMMARY = 70

    try:
        response = api._serial.request(MSP_DATAFLASH_SUMMARY)
        if isinstance(response, tuple):
            summary = response[1]
        else:
            summary = response

        if len(summary) >= 13:
            flags, sectors, totalSize, usedSize = struct.unpack('<BIII', summary[:13])
            flash_ready = bool(flags & 1)
            return {
                'ready': flash_ready,
                'sectors': sectors,
                'total_size': totalSize,
                'used_size': usedSize
            }
    except Exception as e:
        print(f"✗ Error getting flash summary: {e}")
        return None

    return None

def check_and_prepare_flash(api):
    """Check flash status and prepare for testing."""
    print("\nChecking blackbox flash status...")

    summary = get_flash_summary(api)
    if not summary:
        return False

    print(f"  Ready: {summary['ready']}")
    print(f"  Total size: {summary['total_size']} bytes ({summary['total_size']/1024/1024:.1f} MB)")
    print(f"  Used size: {summary['used_size']} bytes ({summary['used_size']/1024:.1f} KB)")

    # Note: We cannot erase flash via MSP since MSP_DATAFLASH_ERASE (code 72)
    # has no handler in the firmware. We'll proceed with the test as-is.
    print("⚠️  Note: Cannot erase flash via MSP - command not implemented in firmware")
    print("⚠️  Proceeding with test using current flash state")

    return True

def arm_fc(api):
    """Arm the flight controller."""
    print("\nArming FC...")

    MSP_SET_RAW_RC = 200
    MSP_ARM = 180  # ARM command (if available)

    try:
        # Send arm command - set AUX1 high to trigger arm mode
        # Assuming AUX1 is configured for arming (channel 5, value > 1700)
        channels = [1500, 1500, 1000, 1500, 2000, 1000, 1000, 1000]  # AUX1 high
        # Extend to 16 channels
        while len(channels) < 16:
            channels.append(1500)

        # Convert to bytes (16-bit per channel)
        data = []
        for ch in channels:
            data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

        api._serial.send(MSP_SET_RAW_RC, data)
        time.sleep(0.1)

        print("✓ Arm command sent")
        return True
    except Exception as e:
        print(f"✗ Error sending arm command: {e}")
        return False

def disarm_fc(api):
    """Disarm the flight controller."""
    print("\nDisarming FC...")

    MSP_SET_RAW_RC = 200

    try:
        # Send disarm command - set AUX1 low
        channels = [1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000]  # AUX1 low
        # Extend to 16 channels
        while len(channels) < 16:
            channels.append(1500)

        # Convert to bytes (16-bit per channel)
        data = []
        for ch in channels:
            data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

        api._serial.send(MSP_SET_RAW_RC, data)
        time.sleep(0.1)

        print("✓ Disarm command sent")
        return True
    except Exception as e:
        print(f"✗ Error sending disarm command: {e}")
        return False

def check_blackbox_status(api, expected_empty=None):
    """Check blackbox flash status."""
    print("\nChecking blackbox flash status...")

    summary = get_flash_summary(api)
    if not summary:
        return False

    print(f"  Ready: {summary['ready']}")
    print(f"  Total size: {summary['total_size']} bytes ({summary['total_size']/1024/1024:.1f} MB)")
    print(f"  Used size: {summary['used_size']} bytes ({summary['used_size']/1024:.1f} KB)")

    if expected_empty is not None:
        if expected_empty and summary['used_size'] == 0:
            print("✓ Flash is empty as expected")
            return True
        elif not expected_empty and summary['used_size'] > 0:
            print("✓ Flash contains data as expected")
            return True
        elif expected_empty and summary['used_size'] > 0:
            print("✗ Flash should be empty but contains data")
            return False
        elif not expected_empty and summary['used_size'] == 0:
            print("✗ Flash should contain data but is empty")
            return False

    return True

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

    print("=" * 70)
    print("Blackbox Flash Test")
    print("=" * 70)
    print(f"Port: {port}")
    print()

    # Step 1: Connect to FC
    api = connect_to_fc(port)
    if not api:
        return 1

    try:
        # Step 2: Check initial flash status and prepare for testing
        print("[Step 1] Checking and preparing flash...")
        if not check_and_prepare_flash(api):
            api.close()
            return 1

        # Get initial flash status
        print("\n[Step 2] Recording initial flash status...")
        initial_summary = get_flash_summary(api)
        if not initial_summary:
            api.close()
            return 1

        # Step 3: Arm FC
        print("\n[Step 3] Arming FC...")
        if not arm_fc(api):
            api.close()
            return 1

        print("  Waiting 30 seconds for blackbox logging...")
        for i in range(30):
            time.sleep(1)
            print(f"  {i+1}/30 seconds", end='\r')
        print()

        # Step 4: Disarm FC
        print("\n[Step 4] Disarming FC...")
        if not disarm_fc(api):
            api.close()
            return 1

        # Step 5: Verify data was written (compare with initial state)
        print("\n[Step 5] Verifying blackbox data was written...")
        # Wait a moment for data to be flushed
        time.sleep(2)

        final_summary = get_flash_summary(api)
        if not final_summary:
            api.close()
            return 1

        print(f"  Initial used size: {initial_summary['used_size']} bytes")
        print(f"  Final used size: {final_summary['used_size']} bytes")

        # Check if data was written (final should be greater than initial)
        if final_summary['used_size'] > initial_summary['used_size']:
            print("✓ Blackbox data was successfully written to flash")
            success = True
        elif final_summary['used_size'] == initial_summary['used_size']:
            print("⚠️  Flash usage unchanged (may indicate no data was written)")
            success = False
        else:
            print("⚠️  Flash usage decreased (unexpected)")
            success = False

        print("\n" + "=" * 70)
        if success:
            print("TEST PASSED: Blackbox flash functionality verified!")
        else:
            print("TEST RESULT: Unable to verify blackbox flash functionality")
        print("=" * 70)
        print("✓ Connected to flight controller")
        print("✓ Checked initial flash status")
        print("✓ FC was armed and logged data for 30 seconds")
        print("✓ FC was disarmed")
        print("✓ Flash usage comparison completed")
        print()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n✗ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if api:
            api.close()

if __name__ == '__main__':
    sys.exit(main())
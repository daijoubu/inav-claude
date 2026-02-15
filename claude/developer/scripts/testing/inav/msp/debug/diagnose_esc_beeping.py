#!/usr/bin/env python3
"""
Diagnose ESC Beeping Issue

This script diagnoses why ESCs are beeping continuously on a physical FC.
Most likely cause: RC receiver signal loss causes failsafe throttle values.

When using MSP as the receiver type, continuous MSP_SET_RAW_RC packets are
required to maintain receiver connection. If these packets stop, the FC
enters failsafe and sends idle/beeping throttle values to ESCs.

This script:
1. Connects to FC via serial port
2. Checks receiver type configuration
3. Monitors receiver status and arming flags
4. Identifies if RC_LINK is causing the issue
5. Provides recommendations

Usage:
    python3 diagnose_esc_beeping.py [port]

Arguments:
    port    Serial port (default: /dev/ttyACM0)

Example:
    python3 diagnose_esc_beeping.py /dev/ttyACM0

Note: If running in sandbox mode, connection may fail due to serial port
restrictions. Retry with dangerouslyDisableSandbox: true if needed.
"""

import sys
import time
from mspapi2 import MSPApi

def diagnose_esc_beeping(port='/dev/ttyACM0'):
    """
    Diagnose ESC beeping issue on physical FC.

    Args:
        port: Serial port (default: /dev/ttyACM0)

    Returns:
        dict with diagnosis results and recommendations
    """

    print("="*60)
    print("ESC Beeping Diagnostic Tool")
    print("="*60)
    print()

    # Step 1: Connect to FC
    print(f"[1/5] Connecting to FC on {port}...")
    try:
        api = MSPApi(port=port, baudrate=115200)
        api.open()
        time.sleep(0.5)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ FAILED to connect: {e}")
        print("\nDiagnostic: Check serial port connection")
        print("  - Is FC plugged in via USB?")
        print("  - Is configurator or other software using the port?")
        print("  - If in sandbox: retry with dangerouslyDisableSandbox: true")
        return {'success': False, 'error': str(e)}

    print()

    # Step 2: Check receiver type
    print("[2/5] Checking receiver configuration...")
    try:
        # Get RX_CONFIG (MSP 44)
        rx_config, _ = api.get_rx_config()

        receiver_type = rx_config.get('receiver_type', 'UNKNOWN')
        print(f"✓ Receiver type: {receiver_type}")

        if receiver_type != 'MSP':
            print("⚠ WARNING: Receiver type is not MSP!")
            print("  For motor wizard with MSP RC, receiver_type should be MSP")
            print("  Current type may not require continuous RC packets")
    except Exception as e:
        print(f"✗ Failed to read receiver config: {e}")
        receiver_type = None

    print()

    # Step 3: Check current RC values
    print("[3/5] Checking current RC channel values...")
    try:
        rc_channels, _ = api.get_rc()

        print(f"  Roll:     {rc_channels.get('roll', 'N/A')}")
        print(f"  Pitch:    {rc_channels.get('pitch', 'N/A')}")
        print(f"  Throttle: {rc_channels.get('throttle', 'N/A')}")
        print(f"  Yaw:      {rc_channels.get('yaw', 'N/A')}")
        print(f"  AUX1:     {rc_channels.get(4, 'N/A')}")

        # Check if channels look like valid data
        throttle = rc_channels.get('throttle', 0)
        if throttle < 900 or throttle > 2100:
            print("⚠ WARNING: Throttle value looks invalid!")
    except Exception as e:
        print(f"✗ Failed to read RC channels: {e}")

    print()

    # Step 4: Check arming flags
    print("[4/5] Checking arming status and blockers...")
    try:
        status, _ = api.get_status_ex()

        arming_flags = status.get('armingDisableFlags', 0)
        is_armed = status.get('armingFlags', 0) & 1  # ARM bit

        print(f"  Armed: {'YES' if is_armed else 'NO'}")
        print(f"  Arming disable flags: 0x{arming_flags:08X}")

        # Check specific flags
        RC_LINK = (1 << 18)  # Bit 18 in armingDisableFlags

        if arming_flags & RC_LINK:
            print("  ✗ RC_LINK blocker is SET - No valid RC signal!")
            print("    This is likely causing the ESC beeping.")
        else:
            print("  ✓ RC_LINK blocker is CLEAR")

        # Decode other common flags
        flag_names = {
            0: "NO_GYRO",
            1: "FAILSAFE",
            2: "RX_FAILSAFE",
            3: "BAD_RX_RECOVERY",
            4: "BOXFAILSAFE",
            5: "RUNAWAY_TAKEOFF",
            6: "CRASH_DETECTED",
            7: "THROTTLE",
            8: "ANGLE",
            9: "BOOT_GRACE_TIME",
            10: "NOPREARM",
            11: "LOAD",
            12: "CALIBRATING",
            13: "CLI",
            14: "CMS_MENU",
            15: "OSD_MENU",
            16: "ROLLPITCH_NOT_CENTERED",
            17: "AUTOTRIM",
            18: "OOM",
            19: "INVALID_SETTING",
            20: "PWM_OUTPUT_ERROR",
            21: "NO_ACC_CAL",
            22: "MOTOR_PROTOCOL",
            23: "ARM_SWITCH",
        }

        active_flags = []
        for bit, name in flag_names.items():
            if arming_flags & (1 << bit):
                active_flags.append(name)

        if active_flags:
            print(f"\n  Active arming blockers: {', '.join(active_flags)}")

    except Exception as e:
        print(f"✗ Failed to read status: {e}")

    print()

    # Step 5: Monitor receiver status over time
    print("[5/5] Monitoring receiver status for 3 seconds...")
    print("  (Checking if RC signal times out...)")

    try:
        for i in range(6):  # 6 samples over 3 seconds
            status, _ = api.get_status_ex()
            arming_flags = status.get('armingDisableFlags', 0)
            has_rc_link = not (arming_flags & (1 << 18))

            print(f"  [{i+1}/6] RC_LINK: {'✓ ACTIVE' if has_rc_link else '✗ LOST'}")
            time.sleep(0.5)
    except Exception as e:
        print(f"✗ Failed to monitor status: {e}")

    api.close()

    print()
    print("="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)
    print()

    # Recommendations
    print("📋 RECOMMENDATIONS:")
    print()

    if receiver_type == 'MSP':
        print("✓ Receiver type is MSP (correct for motor wizard testing)")
        print()
        print("🔧 SOLUTION: Run continuous MSP RC sender to prevent failsafe")
        print()
        print("   The FC needs continuous MSP_SET_RAW_RC packets at ~50Hz")
        print("   to maintain RC link and prevent ESC beeping.")
        print()
        print("   Run this script:")
        print(f"   python3 idle_msp_rc_sender.py {port}")
        print()
        print("   This will send neutral/idle RC values continuously,")
        print("   keeping the receiver active without arming or moving motors.")
        print()
        print("   While that script runs, you can use the motor wizard")
        print("   in the configurator to test individual motors.")
    else:
        print(f"⚠ Receiver type is '{receiver_type}' (not MSP)")
        print()
        print("   If you're testing the motor wizard with MSP as receiver,")
        print("   you need to configure:")
        print("   1. Set 'receiver_type = MSP' in CLI or configurator")
        print("   2. Save and reboot FC")
        print("   3. Run continuous MSP RC sender script")

    print()

    return {'success': True}

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

    try:
        result = diagnose_esc_beeping(port)
        sys.exit(0 if result.get('success') else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

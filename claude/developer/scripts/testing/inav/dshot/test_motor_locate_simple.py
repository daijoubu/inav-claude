#!/usr/bin/env python3
"""
Minimal test script for MSP2_INAV_MOTOR_LOCATE.

Quick test to verify the MSP command works. No fancy error handling,
just sends the command and exits.

Usage:
    python3 test_motor_locate_simple.py /dev/ttyACM0 0
    python3 test_motor_locate_simple.py localhost:5760 0
    python3 test_motor_locate_simple.py /dev/ttyACM0 255  # Stop
"""

import sys
import struct
import time

try:
    from mspapi2 import MSPApi
except ImportError:
    print("ERROR: mspapi2 not installed")
    print("Run: pip install -e ~/Documents/planes/inavflight/mspapi2")
    sys.exit(1)

MSP2_INAV_MOTOR_LOCATE = 0x2042

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <port|tcp> <motor_index>")
        print(f"Example: {sys.argv[0]} /dev/ttyACM0 0")
        print(f"Example: {sys.argv[0]} localhost:5760 255  # Stop")
        sys.exit(1)

    connection = sys.argv[1]
    motor_index = int(sys.argv[2])

    print(f"Connecting to {connection}...")

    # Connect
    if ':' in connection:
        api = MSPApi(tcp_endpoint=connection)
    else:
        api = MSPApi(port=connection, baudrate=115200)

    try:
        api.open()
        print("✓ Connected")

        # Verify responding
        info, version = api.get_api_version()
        print(f"✓ FC API {version['apiVersionMajor']}.{version['apiVersionMinor']}")

        # Check armed
        info, status = api.get_status()
        is_armed = bool(status['armingFlags'] & 0x01)

        if is_armed:
            print("✗ FC is ARMED - aborting!")
            sys.exit(1)
        else:
            print("✓ FC is disarmed")

        # Send locate command
        payload = struct.pack('<B', motor_index)
        response = api.transport.request(MSP2_INAV_MOTOR_LOCATE, payload)

        if motor_index == 255:
            print("✓ Sent STOP command")
        else:
            print(f"✓ Sent locate command for motor {motor_index}")
            print("  Listening... (motor should jerk then beep 4 times over ~2 seconds)")
            time.sleep(2.5)

            # Auto-stop
            payload = struct.pack('<B', 255)
            api.transport.request(MSP2_INAV_MOTOR_LOCATE, payload)
            print("✓ Sent auto-stop")

        api.close()
        print("\nDone! Did the motor beep?")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Arm Physical FC via MSP

Configures physical FC for arming and sends ARM command via RC channels.
Uses HITL mode to bypass sensor calibration requirements.

Adapted from arm_sitl.py for use with physical FC on /dev/ttyACM0.
"""

import sys
import time
import struct
from mspapi2 import MSPApi

def arm_fc(port='/dev/ttyACM0', duration=10):
    """
    Arm physical FC via MSP and keep armed for specified duration.

    Args:
        port: Serial port (default: /dev/ttyACM0)
        duration: How long to keep armed in seconds (default: 10)
    """

    print(f"Connecting to FC on {port}...")
    api = MSPApi(port=port, baudrate=115200)
    api.open()
    time.sleep(0.5)

    print("✓ Connected")

    # Enable HITL mode (bypasses sensor calibration)
    print("Enabling HITL mode...")
    MSP_SIMULATOR = 0x201F
    hitl_data = struct.pack('<B', 1)  # Simple 1-byte payload
    api._serial.send(MSP_SIMULATOR, hitl_data)
    time.sleep(0.5)

    # Send RC channels with ARM enabled (channel 5 > 1500)
    print(f"Arming FC for {duration} seconds...")
    channels = [1500] * 18  # All channels at midpoint
    channels[4] = 1800  # AUX1 (channel 5) high = ARM

    rc_data = struct.pack('<' + 'H' * 18, *channels)

    # Send RC frames at 50Hz for specified duration
    frames = duration * 50
    for i in range(frames):
        api._serial.send(200, rc_data)  # MSP_SET_RAW_RC
        try:
            api._serial.recv()  # Consume response to prevent buffer overflow
        except:
            pass

        if i % 50 == 0 and i > 0:  # Progress every second
            print(f"  {i//50}/{duration} seconds...")

        time.sleep(0.02)

    # Disarm
    print("Disarming...")
    channels[4] = 1000  # AUX1 low = DISARM
    rc_data = struct.pack('<' + 'H' * 18, *channels)

    for i in range(50):  # 1 second of disarm
        api._serial.send(200, rc_data)
        try:
            api._serial.recv()
        except:
            pass
        time.sleep(0.02)

    api.close()
    print("✓ Done")
    return True

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    success = arm_fc(port, duration)
    sys.exit(0 if success else 1)

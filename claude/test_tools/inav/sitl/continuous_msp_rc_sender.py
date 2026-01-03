#!/usr/bin/env python3
"""
Continuous MSP RC Sender for Physical FC

Sends continuous MSP_SET_RAW_RC frames to a physical flight controller
to keep it armed and logging blackbox data.

Similar to crsf_rc_sender.py but uses MSP protocol over serial port.
Does NOT use HITL mode so sensors must calibrate naturally and blackbox
logging works properly.

USAGE:
    python3 continuous_msp_rc_sender.py [port] [--duration SEC] [--rate HZ]

ARGUMENTS:
    port              Serial port (default: /dev/ttyACM0)
    --duration SEC    Duration in seconds (default: 30)
    --rate HZ         Frame rate in Hz (default: 50)

EXAMPLES:
    # Send for 30 seconds at 50Hz
    python3 continuous_msp_rc_sender.py /dev/ttyACM0

    # Send for 60 seconds at 100Hz
    python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 60 --rate 100

PREREQUISITES:
    - FC must have MSP receiver configured (rx_spi_protocol = MSP)
    - ARM mode must be configured on AUX1
    - Sensors must be calibrated (or calibration requirement disabled)
    - Blackbox should be configured to log to SPIFLASH

BEHAVIOR:
    - Connects to FC via serial port
    - Waits 5 seconds with throttle low, disarmed (sensor calibration)
    - Arms the FC (AUX1 > 1700)
    - Keeps FC armed for specified duration
    - Disarms and exits
    - Sends RC frames at specified rate (default 50Hz)
    - Consumes MSP responses to prevent buffer overflow
"""

import struct
import sys
import time
import argparse
from mspapi2 import MSPApi

def send_continuous_rc(port='/dev/ttyACM0', duration=30, rate_hz=50):
    """
    Send continuous MSP RC frames to physical FC.

    Args:
        port: Serial port (default: /dev/ttyACM0)
        duration: How long to stay armed in seconds (default: 30)
        rate_hz: RC frame rate in Hz (default: 50)
    """

    print(f"=== Continuous MSP RC Sender ===")
    print(f"Port: {port}")
    print(f"Duration: {duration}s")
    print(f"Rate: {rate_hz} Hz")
    print()

    print(f"Connecting to FC on {port}...")
    api = MSPApi(port=port, baudrate=115200)
    api.open()
    time.sleep(0.5)
    print("✓ Connected")
    print()

    # Phase 1: Wait for sensor calibration (5 seconds, disarmed, low throttle)
    print("Phase 1: Waiting for sensor calibration (5 seconds)...")
    print("  Throttle: LOW (1000)")
    print("  AUX1: LOW (1000) - DISARMED")
    print()

    channels = [1500] * 18  # All at midpoint
    channels[2] = 1000      # Throttle (channel 3) LOW
    channels[4] = 1000      # AUX1 (channel 5) LOW = DISARM

    rc_data = struct.pack('<' + 'H' * 18, *channels)
    frame_interval = 1.0 / rate_hz

    calibration_frames = int(5 * rate_hz)
    for i in range(calibration_frames):
        api._serial.send(200, rc_data)  # MSP_SET_RAW_RC
        try:
            api._serial.recv()  # Consume response
        except:
            pass

        if i % rate_hz == 0:
            print(f"  {i//rate_hz + 1}/5 seconds...")

        time.sleep(frame_interval)

    print()
    print("Phase 2: Arming FC...")
    print("  Throttle: LOW (1000)")
    print("  AUX1: HIGH (1800) - ARMED")
    print()

    # Phase 2: Arm with low throttle
    channels[4] = 1800  # AUX1 HIGH = ARM
    rc_data = struct.pack('<' + 'H' * 18, *channels)

    arm_frames = int(2 * rate_hz)  # 2 seconds to arm
    for i in range(arm_frames):
        api._serial.send(200, rc_data)
        try:
            api._serial.recv()
        except:
            pass
        time.sleep(frame_interval)

    print("Phase 3: Armed flight...")
    print("  Throttle: MID (1600)")
    print("  AUX1: HIGH (1800) - ARMED")
    print()

    # Phase 3: Armed with mid throttle
    channels[2] = 1600  # Throttle MID
    rc_data = struct.pack('<' + 'H' * 18, *channels)

    flight_frames = int(duration * rate_hz)
    start_time = time.time()

    for i in range(flight_frames):
        api._serial.send(200, rc_data)
        try:
            api._serial.recv()
        except:
            pass

        if i % (rate_hz * 5) == 0:  # Every 5 seconds
            elapsed = time.time() - start_time
            print(f"  {elapsed:.0f}/{duration}s - Frame {i}/{flight_frames}")

        time.sleep(frame_interval)

    print()
    print("Phase 4: Disarming...")

    # Phase 4: Disarm
    channels[2] = 1000  # Throttle LOW
    channels[4] = 1000  # AUX1 LOW = DISARM
    rc_data = struct.pack('<' + 'H' * 18, *channels)

    disarm_frames = int(1 * rate_hz)  # 1 second
    for i in range(disarm_frames):
        api._serial.send(200, rc_data)
        try:
            api._serial.recv()
        except:
            pass
        time.sleep(frame_interval)

    api.close()

    total_time = time.time() - start_time
    total_frames = calibration_frames + arm_frames + flight_frames + disarm_frames

    print()
    print("="*50)
    print("COMPLETE")
    print("="*50)
    print(f"Total time: {total_time:.1f}s")
    print(f"Total frames sent: {total_frames}")
    print(f"Average rate: {total_frames/total_time:.1f} Hz")
    print()
    print("✓ Done")
    print()
    print("Next steps:")
    print("  1. Download blackbox: ./download_blackbox_from_fc.py")
    print("  2. Decode log: blackbox_decode <file>.TXT")

    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send continuous MSP RC to physical FC')
    parser.add_argument('port', type=str, nargs='?', default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Armed duration in seconds (default: 30)')
    parser.add_argument('--rate', type=int, default=50,
                       help='Frame rate in Hz (default: 50)')

    args = parser.parse_args()

    success = send_continuous_rc(args.port, args.duration, args.rate)
    sys.exit(0 if success else 1)

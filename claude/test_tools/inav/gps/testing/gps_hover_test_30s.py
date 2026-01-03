#!/usr/bin/env python3
"""
Configurable Hover Test for navEPH Capture and Blackbox Logging

Simplified test that:
1. Arms the FC
2. Sends constant GPS position for configurable duration
3. Allows position estimator to stabilize
4. Captures navEPH data for frequency analysis
5. Properly disarms the FC to stop blackbox logging

Usage:
    python3 gps_hover_test_30s.py /dev/ttyACM0 [--duration SECONDS]

    Default duration: 20 seconds

Examples:
    python3 gps_hover_test_30s.py /dev/ttyACM0                # 20 seconds (default)
    python3 gps_hover_test_30s.py /dev/ttyACM0 --duration 5   # 5 seconds (for high-field-count tests)
    python3 gps_hover_test_30s.py /dev/ttyACM0 --duration 30  # 30 seconds (for low-field-count tests)

Important:
    - Always let the script complete fully to ensure proper disarming. The total script time needs to be at least 25 seconds longer than the "duration" parameter.
    - Do NOT kill the script with timeout/Ctrl+C - this prevents disarm and FC keeps logging
    - Use shorter durations (5-10s) when testing many blackbox fields to avoid flash overflow
"""

import struct
import time
import sys
import argparse

# MSP protocol constants
MSP_SET_RAW_GPS = 201
MSP_SET_RAW_RC = 200
MSP_SIMULATOR = 0x201F
MSP_EEPROM_WRITE = 250
MSP_SET_MODE_RANGE = 35
MSP_SET_RX_CONFIG = 45
MSP_RX_CONFIG = 44
MSP_REBOOT = 68

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# Test location (London)
BASE_LAT = int(51.5074 * 1e7)
BASE_LON = int(-0.1278 * 1e7)
BASE_ALT = 50  # meters


def consume_response(board):
    """Consume MSP response to prevent buffer overflow."""
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass


def send_rc(board, throttle=RC_LOW, roll=RC_MID, pitch=RC_MID, yaw=RC_MID,
            aux1=RC_LOW, aux2=RC_LOW, aux3=RC_LOW, aux4=RC_LOW):
    """Send RC channel values via MSP."""
    channels = [roll, pitch, throttle, yaw, aux1, aux2, aux3, aux4]
    while len(channels) < 16:
        channels.append(RC_MID)

    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    consume_response(board)


def send_gps(board, fix_type, num_sat, lat, lon, alt_m, ground_speed):
    """Send GPS data via MSP."""
    payload = list(struct.pack('<BBiiHH',
        fix_type, num_sat, lat, lon, alt_m, ground_speed))
    board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
    consume_response(board)


def setup_receiver_type(board):
    """Set receiver type to MSP."""
    board.send_RAW_msg(MSP_RX_CONFIG, data=[])
    time.sleep(0.2)
    dataHandler = board.receive_msg()
    data = dataHandler.get('dataView', []) if dataHandler else []

    if data and len(data) >= 24:
        current_data = list(data)
    else:
        current_data = [0] * 24
        current_data[1], current_data[2] = 0x6C, 0x07
        current_data[3], current_data[4] = 0xDC, 0x05
        current_data[5], current_data[6] = 0x4C, 0x04
        current_data[8], current_data[9] = 0x75, 0x03
        current_data[10], current_data[11] = 0x43, 0x08

    current_data[23] = 2  # RX_TYPE_MSP
    board.send_RAW_msg(MSP_SET_RX_CONFIG, data=current_data[:24])
    consume_response(board)


def setup_arm_mode(board):
    """Configure ARM mode on AUX1."""
    payload = [0, 0, 0, 32, 48]  # slot=0, ARM=0, AUX1, 1700-2100us
    board.send_RAW_msg(MSP_SET_MODE_RANGE, data=payload)
    consume_response(board)


def save_config(board):
    """Save configuration to EEPROM."""
    board.send_RAW_msg(MSP_EEPROM_WRITE, data=[])
    time.sleep(0.5)
    consume_response(board)


def enable_hitl_mode(board):
    """Enable HITL mode."""
    payload = [2, 1]  # MSP version 2, HITL enable
    board.send_RAW_msg(MSP_SIMULATOR, data=payload)
    consume_response(board)


def main():
    parser = argparse.ArgumentParser(description='Hover test for navEPH and blackbox logging')
    parser.add_argument('target', help='Serial port or TCP port')
    parser.add_argument('--duration', type=int, default=20, help='Hover duration in seconds (default: 20)')
    args = parser.parse_args()

    try:
        from unavlib.main import MSPy
    except ImportError:
        print("Error: uNAVlib not installed")
        return 1

    # Determine connection type
    try:
        port = int(args.target)
        use_tcp = True
        device = str(port)
    except ValueError:
        use_tcp = False
        device = args.target

    print(f"Connecting to {device}...")

    try:
        # Setup
        print("\n[Setup] Configuring FC...")
        with MSPy(device=device, use_tcp=use_tcp, loglevel='WARNING') as board:
            if board == 1:
                print("Error: Connection failed")
                return 1

            print(f"Connected to {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")
            setup_receiver_type(board)
            setup_arm_mode(board)
            save_config(board)
            print("Rebooting FC...")
            board.send_RAW_msg(MSP_REBOOT, data=[])

        boot_time = time.time()

        print(f"time since boot: {int(time.time() - boot_time)}s")
        print("Waiting 15 seconds for reboot...")
        time.sleep(15)
        print(f"time: {int(time.time() - boot_time)}s")

        # Test
        print(f"\n[Test] Running {args.duration}-second hover...")
        with MSPy(device=device, use_tcp=use_tcp, loglevel='WARNING') as board:
            if board == 1:
                print("Error: Reconnection failed")
                return 1

            print("Reconnected!")
            enable_hitl_mode(board)

            print(f"time: {int(time.time() - boot_time)}s")
            # Phase 1: Pre-arm GPS lock (2 seconds)
            print("\n[Phase 1] Establishing GPS lock (2s)...")
            start = time.time()
            while time.time() - start < 2.0:
                send_gps(board, fix_type=2, num_sat=12, lat=BASE_LAT,
                lon=BASE_LON, alt_m=BASE_ALT, ground_speed=0)
                send_rc(board, throttle=RC_LOW, aux1=RC_LOW)
                time.sleep(0.02)  # 50 Hz

            print(f"time: {int(time.time() - boot_time)}s")
            # Phase 2: Arm (2 seconds)
            print("[Phase 2] Arming FC (2s)...")
            start = time.time()
            while time.time() - start < 2.0:
                send_gps(board, fix_type=2, num_sat=12, lat=BASE_LAT,
                        lon=BASE_LON, alt_m=BASE_ALT, ground_speed=0)
                send_rc(board, throttle=RC_LOW, aux1=RC_HIGH)  # ARM
                time.sleep(0.02)


            print(f"time: {int(time.time() - boot_time)}s")
            # Phase 3: Armed hover (configurable duration)
            print(f"[Phase 3] Armed hover ({args.duration}s) - blackbox logging...")
            start = time.time()
            last_status = 0

            while time.time() - start < args.duration:
                send_gps(board, fix_type=2, num_sat=12, lat=BASE_LAT,
                        lon=BASE_LON, alt_m=BASE_ALT, ground_speed=0)
                send_rc(board, throttle=1200, aux1=RC_HIGH)  # Armed, low throttle
                time.sleep(0.02)

                # Status every 5 seconds
                elapsed = time.time() - start
                if int(elapsed / 5) > last_status:
                    last_status = int(elapsed / 5)
                    print(f"  {elapsed:.0f}s / {args.duration}s...")

            print(f"time: {int(time.time() - boot_time)}s")
            # Phase 4: Disarm (1 second)
            print("[Phase 4] Disarming...")
            start = time.time()
            while time.time() - start < 1.0:
                send_gps(board, fix_type=2, num_sat=12, lat=BASE_LAT,
                        lon=BASE_LON, alt_m=BASE_ALT, ground_speed=0)
                send_rc(board, throttle=RC_LOW, aux1=RC_LOW)  # DISARM
                time.sleep(0.02)

            print("\n✓ Test complete!")
            print("\nNext steps:")
            print("1. Download blackbox log via INAV Configurator")
            print("2. Decode: blackbox_decode <file.TXT>")
            print("3. Analyze: python3 analyze_naveph_spectrum.py <file.csv>")

            return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

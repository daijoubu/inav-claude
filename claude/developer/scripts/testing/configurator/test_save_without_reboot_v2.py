#!/usr/bin/env python3
"""
Test if saving board alignment without reboot affects MSP_RAW_IMU data
Using mspapi2 library
"""

import sys
import time
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPApi

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_save_without_reboot_v2.py <port>")
        print("Example: python3 test_save_without_reboot_v2.py /dev/ttyACM0")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    print(f"Connecting to {port} at {baudrate}...")
    api = MSPApi(port=port, baudrate=baudrate)
    api.open()
    time.sleep(0.5)
    print("Connected!\n")

    print("=" * 70)
    print("TEST: Does saving alignment without reboot affect MSP_RAW_IMU?")
    print("=" * 70)

    # Step 1: Read current alignment
    print("\n[1] Reading current FC alignment...")
    try:
        alignment = api.get_board_alignment()
        print(f"    Current: pitch={alignment['pitch']}°, roll={alignment['roll']}°, yaw={alignment['yaw']}°")
        original = alignment.copy()
    except Exception as e:
        print(f"    ERROR: {e}")
        print("    Trying to continue anyway...")
        original = {'pitch': 0, 'roll': 0, 'yaw': 0}

    # Step 2: Read IMU at current alignment
    print("\n[2] Reading MSP_RAW_IMU at current alignment...")
    print("    Keep board FLAT on table!")
    time.sleep(2)

    imu1 = api.get_raw_imu()
    print(f"    Accel: [{imu1['acc'][0]:6.3f}, {imu1['acc'][1]:6.3f}, {imu1['acc'][2]:6.3f}] g")

    # Step 3: Set to 90° yaw
    print("\n[3] Setting FC to yaw=90° and saving...")
    try:
        api.set_board_alignment(pitch=0, roll=0, yaw=90)
        api.save_to_eeprom()
        time.sleep(0.5)

        # Verify
        alignment = api.get_board_alignment()
        print(f"    Confirmed: pitch={alignment['pitch']}°, roll={alignment['roll']}°, yaw={alignment['yaw']}°")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Step 4: Read IMU with 90° yaw
    print("\n[4] Reading MSP_RAW_IMU with FC at yaw=90°...")
    print("    (Board still FLAT)")
    time.sleep(1)

    imu2 = api.get_raw_imu()
    print(f"    Accel: [{imu2['acc'][0]:6.3f}, {imu2['acc'][1]:6.3f}, {imu2['acc'][2]:6.3f}] g")

    # Step 5: Set to 0,0,0 WITHOUT reboot
    print("\n[5] Setting FC to 0,0,0 and saving (NO REBOOT)...")
    try:
        api.set_board_alignment(pitch=0, roll=0, yaw=0)
        api.save_to_eeprom()
        time.sleep(0.5)

        # Verify
        alignment = api.get_board_alignment()
        print(f"    Confirmed: pitch={alignment['pitch']}°, roll={alignment['roll']}°, yaw={alignment['yaw']}°")
    except Exception as e:
        print(f"    ERROR: {e}")

    # Step 6: Read IMU with 0,0,0
    print("\n[6] Reading MSP_RAW_IMU with FC at 0,0,0...")
    print("    (Board still FLAT)")
    time.sleep(1)

    imu3 = api.get_raw_imu()
    print(f"    Accel: [{imu3['acc'][0]:6.3f}, {imu3['acc'][1]:6.3f}, {imu3['acc'][2]:6.3f}] g")

    # Step 7: Compare
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Original alignment: [{imu1['acc'][0]:6.3f}, {imu1['acc'][1]:6.3f}, {imu1['acc'][2]:6.3f}]")
    print(f"With yaw=90°:       [{imu2['acc'][0]:6.3f}, {imu2['acc'][1]:6.3f}, {imu2['acc'][2]:6.3f}]")
    print(f"With yaw=0°:        [{imu3['acc'][0]:6.3f}, {imu3['acc'][1]:6.3f}, {imu3['acc'][2]:6.3f}]")

    diff_1_2 = max(abs(imu1['acc'][i] - imu2['acc'][i]) for i in range(3))
    diff_2_3 = max(abs(imu2['acc'][i] - imu3['acc'][i]) for i in range(3))

    print(f"\nMax diff (original → yaw=90°): {diff_1_2:.3f} g")
    print(f"Max diff (yaw=90° → yaw=0°):   {diff_2_3:.3f} g")

    if diff_2_3 < 0.05:
        print("\n✗ NO CHANGE - Reboot required for alignment to take effect")
    else:
        print("\n✓ DATA CHANGED - Alignment takes effect immediately without reboot!")

    # Restore original alignment
    print(f"\n[7] Restoring original alignment: {original['pitch']}°, {original['roll']}°, {original['yaw']}°...")
    try:
        api.set_board_alignment(pitch=original['pitch'], roll=original['roll'], yaw=original['yaw'])
        api.save_to_eeprom()
        time.sleep(0.5)

        alignment = api.get_board_alignment()
        print(f"    Restored: pitch={alignment['pitch']}°, roll={alignment['roll']}°, yaw={alignment['yaw']}°")
    except Exception as e:
        print(f"    ERROR: {e}")

    api.close()
    print("\nDone!")

if __name__ == '__main__':
    main()

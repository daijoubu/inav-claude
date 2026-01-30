#!/usr/bin/env python3
"""
Test if saving board alignment without reboot affects MSP_RAW_IMU data

This tests whether the firmware updates its transformation matrix
when we save alignment settings, or if a reboot is required.
"""

import serial
import struct
import time
import sys

MSP_HEADER = b'$M<'
MSP_RAW_IMU = 102
MSP_BOARD_ALIGNMENT = 242
MSP_SET_BOARD_ALIGNMENT = 243
MSP_EEPROM_WRITE = 250

def calculate_checksum(size, cmd, data=b''):
    checksum = size ^ cmd
    for byte in data:
        checksum ^= byte
    return checksum

def build_msp_request(cmd, data=b''):
    size = len(data)
    checksum = calculate_checksum(size, cmd, data)
    return MSP_HEADER + struct.pack('BB', size, cmd) + data + struct.pack('B', checksum)

def parse_msp_response(data):
    if len(data) < 6:
        return None
    idx = data.find(b'$M>')
    if idx < 0:
        return None
    if len(data) < idx + 6:
        return None
    size = data[idx + 3]
    cmd = data[idx + 4]
    if len(data) < idx + 5 + size + 1:
        return None
    payload = data[idx + 5 : idx + 5 + size]
    return (cmd, payload)

def read_raw_imu(ser):
    """Read accelerometer from MSP_RAW_IMU"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_RAW_IMU))
    time.sleep(0.05)
    response = ser.read(64)
    result = parse_msp_response(response)
    if result is None or result[0] != MSP_RAW_IMU:
        return None
    payload = result[1]
    if len(payload) < 18:
        return None
    values = struct.unpack('<hhhhhhhhh', payload[:18])
    return {
        'acc': [values[0] / 512.0, values[1] / 512.0, values[2] / 512.0],
        'gyro': [values[3], values[4], values[5]],
        'mag': [values[6], values[7], values[8]]
    }

def read_board_alignment(ser):
    """Read current board alignment settings"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_BOARD_ALIGNMENT))
    time.sleep(0.05)
    response = ser.read(64)
    result = parse_msp_response(response)
    if result is None or result[0] != MSP_BOARD_ALIGNMENT:
        return None
    payload = result[1]
    if len(payload) < 6:
        return None
    values = struct.unpack('<hhh', payload[:6])
    return {
        'pitch': values[0] // 10,
        'roll': values[1] // 10,
        'yaw': values[2] // 10
    }

def set_board_alignment(ser, pitch, roll, yaw):
    """Set board alignment (in degrees)"""
    data = struct.pack('<hhh', pitch * 10, roll * 10, yaw * 10)
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_SET_BOARD_ALIGNMENT, data))
    time.sleep(0.1)
    response = ser.read(64)
    return parse_msp_response(response) is not None

def save_eeprom(ser):
    """Save settings to EEPROM"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_EEPROM_WRITE))
    time.sleep(0.5)  # EEPROM write takes time
    response = ser.read(64)
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_save_without_reboot.py <port>")
        print("Example: python3 test_save_without_reboot.py /dev/ttyACM0")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    print(f"Connecting to {port} at {baudrate}...")
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(0.5)
    print("Connected!\n")

    print("=" * 70)
    print("TEST: Does saving alignment without reboot affect MSP_RAW_IMU?")
    print("=" * 70)

    # Step 1: Read and save original alignment
    print("\n[1] Reading current FC alignment...")
    original = read_board_alignment(ser)
    if not original:
        print("ERROR: Failed to read board alignment")
        sys.exit(1)
    print(f"    Current: pitch={original['pitch']}°, roll={original['roll']}°, yaw={original['yaw']}°")

    # Step 2: Set to 90° yaw
    print("\n[2] Setting FC to yaw=90° and saving...")
    if not set_board_alignment(ser, 0, 0, 90):
        print("ERROR: Failed to set alignment")
        sys.exit(1)
    save_eeprom(ser)
    time.sleep(0.5)

    # Verify it saved
    current = read_board_alignment(ser)
    print(f"    Confirmed: pitch={current['pitch']}°, roll={current['roll']}°, yaw={current['yaw']}°")

    # Step 3: Read MSP_RAW_IMU with 90° yaw
    print("\n[3] Reading MSP_RAW_IMU with FC at yaw=90°...")
    print("    Keep board FLAT on table!")
    time.sleep(2)

    imu_with_90 = read_raw_imu(ser)
    if not imu_with_90:
        print("ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Accel: [{imu_with_90['acc'][0]:6.3f}, {imu_with_90['acc'][1]:6.3f}, {imu_with_90['acc'][2]:6.3f}] g")

    # Step 4: Set to 0,0,0 WITHOUT reboot
    print("\n[4] Setting FC to 0,0,0 and saving (NO REBOOT)...")
    if not set_board_alignment(ser, 0, 0, 0):
        print("ERROR: Failed to set alignment")
        sys.exit(1)
    save_eeprom(ser)
    time.sleep(0.5)

    # Verify it saved
    current = read_board_alignment(ser)
    print(f"    Confirmed: pitch={current['pitch']}°, roll={current['roll']}°, yaw={current['yaw']}°")

    # Step 5: Read MSP_RAW_IMU with 0,0,0
    print("\n[5] Reading MSP_RAW_IMU with FC at 0,0,0...")
    print("    (Board should still be FLAT)")
    time.sleep(1)

    imu_with_00 = read_raw_imu(ser)
    if not imu_with_00:
        print("ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Accel: [{imu_with_00['acc'][0]:6.3f}, {imu_with_00['acc'][1]:6.3f}, {imu_with_00['acc'][2]:6.3f}] g")

    # Step 6: Compare
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"MSP_RAW_IMU with yaw=90°: [{imu_with_90['acc'][0]:6.3f}, {imu_with_90['acc'][1]:6.3f}, {imu_with_90['acc'][2]:6.3f}]")
    print(f"MSP_RAW_IMU with yaw=0°:  [{imu_with_00['acc'][0]:6.3f}, {imu_with_00['acc'][1]:6.3f}, {imu_with_00['acc'][2]:6.3f}]")

    diff_x = abs(imu_with_90['acc'][0] - imu_with_00['acc'][0])
    diff_y = abs(imu_with_90['acc'][1] - imu_with_00['acc'][1])
    diff_z = abs(imu_with_90['acc'][2] - imu_with_00['acc'][2])
    max_diff = max(diff_x, diff_y, diff_z)

    print(f"\nDifference: [{diff_x:.3f}, {diff_y:.3f}, {diff_z:.3f}] g")
    print(f"Max difference: {max_diff:.3f} g")

    if max_diff < 0.05:
        print("\n✗ NO CHANGE - Reboot required for alignment to take effect")
    else:
        print("\n✓ DATA CHANGED - Alignment takes effect immediately without reboot!")

    # Restore original alignment
    print(f"\n[6] Restoring original alignment: {original['pitch']}°, {original['roll']}°, {original['yaw']}°...")
    set_board_alignment(ser, original['pitch'], original['roll'], original['yaw'])
    save_eeprom(ser)
    time.sleep(0.5)
    final = read_board_alignment(ser)
    print(f"    Restored: pitch={final['pitch']}°, roll={final['roll']}°, yaw={final['yaw']}°")

    ser.close()
    print("\nDone!")

if __name__ == '__main__':
    main()

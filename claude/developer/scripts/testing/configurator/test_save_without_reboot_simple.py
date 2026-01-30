#!/usr/bin/env python3
"""
Test if saving board alignment without reboot affects MSP_RAW_IMU data
Using raw MSP (same as alignment_test.py which works)
"""

import serial
import struct
import time
import sys
import math

MSP_HEADER = b'$M<'
MSP_RAW_IMU = 102
MSP_BOARD_ALIGNMENT = 38
MSP_SET_BOARD_ALIGNMENT = 39
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
    return [values[0] / 512.0, values[1] / 512.0, values[2] / 512.0]

def set_board_alignment(ser, pitch, roll, yaw):
    """Set board alignment (in degrees, converts to decidegrees internally)"""
    # Convert to decidegrees
    pitch_dd = pitch * 10
    roll_dd = roll * 10
    yaw_dd = yaw * 10

    # Convert signed to unsigned for MSP protocol
    # Negative values wrap around: -900 becomes 65536-900=64636
    def to_u16(val):
        return val if val >= 0 else 65536 + val

    data = struct.pack('<HHH', to_u16(pitch_dd), to_u16(roll_dd), to_u16(yaw_dd))
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_SET_BOARD_ALIGNMENT, data))
    time.sleep(0.1)
    response = ser.read(64)
    # Check for error response ($M!)
    if b'$M!' in response:
        return False
    return True

def save_eeprom(ser):
    """Save settings to EEPROM"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_EEPROM_WRITE))
    time.sleep(1.0)  # EEPROM write can take a while
    response = ser.read(64)
    if b'$M!' in response:
        return False
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_save_without_reboot_simple.py <port>")
        print("Example: python3 test_save_without_reboot_simple.py /dev/ttyACM0")
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
    print("\nIMPORTANT: Keep the board FLAT on the table for entire test!\n")
    input("Press Enter to start...")

    # Step 1: Read IMU at current alignment
    print("\n[1] Reading MSP_RAW_IMU at current FC alignment...")
    time.sleep(1)
    imu1 = read_raw_imu(ser)
    if not imu1:
        print("ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Accel: [{imu1[0]:7.3f}, {imu1[1]:7.3f}, {imu1[2]:7.3f}] g")

    # Step 2: Set to roll=180° (upside down)
    print("\n[2] Setting FC to roll=180° and saving...")
    if not set_board_alignment(ser, 0, 180, 0):
        print("    WARNING: Set alignment command failed or not supported")
    if not save_eeprom(ser):
        print("    WARNING: Save EEPROM failed")
    time.sleep(0.5)

    # Step 3: Read IMU with roll=180° (NO REBOOT)
    print("\n[3] Reading MSP_RAW_IMU after save (NO REBOOT)...")
    print("    If transform applied: Z should flip sign!")
    time.sleep(1)
    imu2 = read_raw_imu(ser)
    if not imu2:
        print("ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Accel: [{imu2[0]:7.3f}, {imu2[1]:7.3f}, {imu2[2]:7.3f}] g")

    # Step 4: Set to 0,0,0
    print("\n[4] Setting FC to 0,0,0 and saving...")
    if not set_board_alignment(ser, 0, 0, 0):
        print("    WARNING: Set alignment command failed")
    if not save_eeprom(ser):
        print("    WARNING: Save EEPROM failed")
    time.sleep(0.5)

    # Step 5: Read IMU with 0,0,0 (NO REBOOT)
    print("\n[5] Reading MSP_RAW_IMU after save (NO REBOOT)...")
    time.sleep(1)
    imu3 = read_raw_imu(ser)
    if not imu3:
        print("ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Accel: [{imu3[0]:7.3f}, {imu3[1]:7.3f}, {imu3[2]:7.3f}] g")

    # Step 6: Compare
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Original:      [{imu1[0]:7.3f}, {imu1[1]:7.3f}, {imu1[2]:7.3f}] g")
    print(f"After roll=180°: [{imu2[0]:7.3f}, {imu2[1]:7.3f}, {imu2[2]:7.3f}] g")
    print(f"After 0,0,0:   [{imu3[0]:7.3f}, {imu3[1]:7.3f}, {imu3[2]:7.3f}] g")

    diff_1_2 = max(abs(imu1[i] - imu2[i]) for i in range(3))
    diff_2_3 = max(abs(imu2[i] - imu3[i]) for i in range(3))
    z_flipped = abs(abs(imu2[2]) - abs(imu1[2])) < 0.1 and imu1[2] * imu2[2] < 0

    print(f"\nMax diff (original → roll=180°): {diff_1_2:.3f} g")
    print(f"Z-axis flipped sign: {z_flipped}")
    print(f"Max diff (roll=180° → 0,0,0):    {diff_2_3:.3f} g")

    if diff_1_2 < 0.05 and diff_2_3 < 0.05:
        print("\n✗ NO CHANGE - Reboot required for alignment to take effect")
        print("   The wizard will need to: set 0,0,0 → save → reboot → detect")
    else:
        print("\n✓ DATA CHANGED - Alignment takes effect immediately!")
        print("   The wizard can detect without rebooting")

    ser.close()
    print("\nDone! (FC left at 0,0,0 alignment)")

if __name__ == '__main__':
    main()

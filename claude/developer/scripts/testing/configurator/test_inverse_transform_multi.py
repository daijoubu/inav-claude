#!/usr/bin/env python3
"""
Test inverse transformation with 8 different alignment values
Automatically tests that the math works for all orientations
"""

import serial
import struct
import time
import sys
import math
import os
import glob

MSP_HEADER = b'$M<'
MSP_RAW_IMU = 102
MSP_BOARD_ALIGNMENT = 38
MSP_SET_BOARD_ALIGNMENT = 39
MSP_EEPROM_WRITE = 250
MSP_REBOOT = 68

# Test alignments to verify
TEST_ALIGNMENTS = [
    {'pitch': 0, 'roll': 0, 'yaw': 0, 'name': 'Identity (0,0,0)'},
    {'pitch': 0, 'roll': 90, 'yaw': 0, 'name': 'Roll 90°'},
    {'pitch': 0, 'roll': 180, 'yaw': 0, 'name': 'Roll 180° (upside down)'},
    {'pitch': 0, 'roll': -90, 'yaw': 0, 'name': 'Roll -90°'},
    {'pitch': 90, 'roll': 0, 'yaw': 0, 'name': 'Pitch 90°'},
    {'pitch': 0, 'roll': 0, 'yaw': 90, 'name': 'Yaw 90°'},
    {'pitch': 0, 'roll': 45, 'yaw': 0, 'name': 'Roll 45°'},
    {'pitch': 0, 'roll': 0, 'yaw': 45, 'name': 'Yaw 45°'},
]

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

def find_fc_device():
    """Find any available /dev/ttyACM* device"""
    devices = glob.glob('/dev/ttyACM*')
    if devices:
        return devices[0]
    return None

def wait_for_fc_after_reboot(original_device, timeout=30):
    """Wait for FC to reappear after reboot, handle device path changes"""
    print(f"    Waiting for FC to disconnect...", end='', flush=True)
    start = time.time()

    # Wait for original device to disappear (up to 5 seconds)
    while os.path.exists(original_device) and (time.time() - start) < 5:
        time.sleep(0.1)

    if os.path.exists(original_device):
        print(" (didn't disconnect)", flush=True)
    else:
        print(" done", flush=True)

    # Wait for any ttyACM device to appear
    print(f"    Waiting for FC to reconnect...", end='', flush=True)
    device = None
    while (time.time() - start) < timeout:
        device = find_fc_device()
        if device:
            break
        time.sleep(0.5)

    if device:
        time.sleep(2)  # Give it time to fully enumerate
        elapsed = time.time() - start
        print(f" {device} ({elapsed:.1f}s)", flush=True)
        return device
    else:
        print(f" FAILED after {timeout}s", flush=True)
        return None

def read_raw_imu(ser):
    """Read accelerometer from MSP_RAW_IMU, average 5 readings"""
    readings = []
    for _ in range(5):
        ser.reset_input_buffer()
        ser.write(build_msp_request(MSP_RAW_IMU))
        time.sleep(0.02)
        response = ser.read(64)
        result = parse_msp_response(response)
        if result and result[0] == MSP_RAW_IMU:
            payload = result[1]
            if len(payload) >= 18:
                values = struct.unpack('<hhhhhhhhh', payload[:18])
                readings.append([values[0] / 512.0, values[1] / 512.0, values[2] / 512.0])
        time.sleep(0.01)

    if not readings:
        return None

    # Average the readings
    avg = [
        sum(r[0] for r in readings) / len(readings),
        sum(r[1] for r in readings) / len(readings),
        sum(r[2] for r in readings) / len(readings)
    ]
    return avg

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
    values = struct.unpack('<HHH', payload[:6])
    def from_u16(val):
        return val if val < 32768 else val - 65536
    return {
        'roll': from_u16(values[0]) / 10.0,
        'pitch': from_u16(values[1]) / 10.0,
        'yaw': from_u16(values[2]) / 10.0
    }

def set_board_alignment(ser, pitch, roll, yaw):
    """Set board alignment (in degrees)"""
    pitch_dd = int(pitch * 10)
    roll_dd = int(roll * 10)
    yaw_dd = int(yaw * 10)

    def to_u16(val):
        return val if val >= 0 else 65536 + val

    data = struct.pack('<HHH', to_u16(roll_dd), to_u16(pitch_dd), to_u16(yaw_dd))
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_SET_BOARD_ALIGNMENT, data))
    time.sleep(0.1)
    response = ser.read(64)
    return not (b'$M!' in response)

def save_eeprom(ser):
    """Save settings to EEPROM"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_EEPROM_WRITE))
    time.sleep(1.0)
    response = ser.read(64)
    return not (b'$M!' in response)

def reboot_fc(ser):
    """Reboot the FC via MSP"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_REBOOT))
    time.sleep(0.1)
    return True

def build_rotation_matrix(roll_deg, pitch_deg, yaw_deg):
    """
    Build rotation matrix matching INAV's rotationMatrixFromAngles()
    Source: inav/src/main/common/maths.c
    """
    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)

    cosx = math.cos(roll)
    sinx = math.sin(roll)
    cosy = math.cos(pitch)
    siny = math.sin(pitch)
    cosz = math.cos(yaw)
    sinz = math.sin(yaw)

    coszcosx = cosz * cosx
    sinzcosx = sinz * cosx
    coszsinx = sinx * cosz
    sinzsinx = sinx * sinz

    # INAV's rotation matrix (matches firmware exactly)
    R = [
        [cosz * cosy,                      -cosy * sinz,                      siny                    ],
        [sinzcosx + (coszsinx * siny),     coszcosx - (sinzsinx * siny),      -sinx * cosy            ],
        [(sinzsinx) - (coszcosx * siny),   (coszsinx) + (sinzcosx * siny),    cosy * cosx             ]
    ]
    return R

def transpose_matrix(R):
    """Transpose a 3x3 matrix (inverse for rotation matrices)"""
    return [
        [R[0][0], R[1][0], R[2][0]],
        [R[0][1], R[1][1], R[2][1]],
        [R[0][2], R[1][2], R[2][2]]
    ]

def apply_rotation(R, vec):
    """
    Apply rotation matrix to a vector (standard matrix multiplication)

    INAV's rotationMatrixRotateVector uses R^T * vec (columns)
    So: transformed = R^T * raw
    To invert: raw = R * transformed (standard multiplication with rows)
    """
    return [
        R[0][0]*vec[0] + R[0][1]*vec[1] + R[0][2]*vec[2],  # Standard: use rows
        R[1][0]*vec[0] + R[1][1]*vec[1] + R[1][2]*vec[2],
        R[2][0]*vec[0] + R[2][1]*vec[1] + R[2][2]*vec[2]
    ]

def main():
    device = find_fc_device()
    if not device:
        print("ERROR: No FC device found")
        sys.exit(1)

    baudrate = 115200
    print(f"Connecting to {device} at {baudrate}...")
    ser = serial.Serial(device, baudrate, timeout=1)
    time.sleep(0.5)
    print("Connected!\n")

    print("=" * 70)
    print("MULTI-ALIGNMENT INVERSE TRANSFORMATION TEST")
    print("=" * 70)
    print(f"\nTesting {len(TEST_ALIGNMENTS)} different alignments")
    print("⚠️  CRITICAL: Keep board FLAT on table, DO NOT TOUCH during test!")
    print(f"   The FC will reboot {len(TEST_ALIGNMENTS) + 2} times.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    # Save original alignment
    print("\n[0] Saving original alignment...")
    original_alignment = read_board_alignment(ser)
    if not original_alignment:
        print("    ERROR: Failed to read alignment")
        sys.exit(1)
    print(f"    Original: roll={original_alignment['roll']:.1f}°, pitch={original_alignment['pitch']:.1f}°, yaw={original_alignment['yaw']:.1f}°")

    # Test each alignment
    results = []
    for i, test_align in enumerate(TEST_ALIGNMENTS):
        print(f"\n[{i+1}/{len(TEST_ALIGNMENTS)}] Testing: {test_align['name']}")
        print(f"    Setting alignment: pitch={test_align['pitch']}°, roll={test_align['roll']}°, yaw={test_align['yaw']}°")

        if not set_board_alignment(ser, test_align['pitch'], test_align['roll'], test_align['yaw']):
            print("    ERROR: Set alignment failed")
            continue
        if not save_eeprom(ser):
            print("    ERROR: Save failed")
            continue

        print("    Rebooting...")
        reboot_fc(ser)
        ser.close()

        device = wait_for_fc_after_reboot(device)
        if not device:
            print("    ERROR: FC did not reconnect")
            sys.exit(1)

        ser = serial.Serial(device, baudrate, timeout=1)
        time.sleep(1)

        # Read transformed data
        print("    Reading IMU data...")
        imu_transformed = read_raw_imu(ser)
        if not imu_transformed:
            print("    ERROR: Failed to read IMU")
            continue

        print(f"    Transformed: [{imu_transformed[0]:7.3f}, {imu_transformed[1]:7.3f}, {imu_transformed[2]:7.3f}] g")

        # Calculate raw using inverse transform
        # INAV applies R^T to get transformed data
        # To invert: apply R (NOT R^T) using standard multiplication
        R = build_rotation_matrix(test_align['roll'], test_align['pitch'], test_align['yaw'])
        imu_raw_calculated = apply_rotation(R, imu_transformed)  # No transpose!

        print(f"    Calculated raw: [{imu_raw_calculated[0]:7.3f}, {imu_raw_calculated[1]:7.3f}, {imu_raw_calculated[2]:7.3f}] g")

        results.append({
            'name': test_align['name'],
            'alignment': test_align,
            'transformed': imu_transformed,
            'calculated_raw': imu_raw_calculated
        })

    # Now set to 0,0,0 and read actual raw data
    print(f"\n[FINAL] Setting to 0,0,0 to verify all calculations...")
    if not set_board_alignment(ser, 0, 0, 0):
        print("    ERROR: Set alignment failed")
        sys.exit(1)
    if not save_eeprom(ser):
        print("    ERROR: Save failed")
        sys.exit(1)

    print("    Rebooting...")
    reboot_fc(ser)
    ser.close()

    device = wait_for_fc_after_reboot(device)
    if not device:
        print("    ERROR: FC did not reconnect")
        sys.exit(1)

    ser = serial.Serial(device, baudrate, timeout=1)
    time.sleep(1)

    print("    Reading actual raw data...")
    imu_actual_raw = read_raw_imu(ser)
    if not imu_actual_raw:
        print("    ERROR: Failed to read IMU")
        sys.exit(1)

    print(f"    Actual raw: [{imu_actual_raw[0]:7.3f}, {imu_actual_raw[1]:7.3f}, {imu_actual_raw[2]:7.3f}] g")

    mag_actual = math.sqrt(imu_actual_raw[0]**2 + imu_actual_raw[1]**2 + imu_actual_raw[2]**2)
    print(f"    Magnitude: {mag_actual:.3f}g")

    if mag_actual < 0.85 or mag_actual > 1.15:
        print(f"\n⚠️  WARNING: Board appears to have moved! Gravity = {mag_actual:.3f}g (expected ~1.0g)")
        print("    Test results may not be valid.")

    # Compare all calculated raw values to EACH OTHER
    # They should all be identical (since board didn't move)
    print("\n" + "=" * 70)
    print("RESULTS: Comparing calculated raw values to each other")
    print("=" * 70)

    # Use first result as reference
    reference = results[0]['calculated_raw']
    print(f"\nReference (from {results[0]['name']}):")
    print(f"  Raw: [{reference[0]:7.3f}, {reference[1]:7.3f}, {reference[2]:7.3f}] g")

    all_passed = True
    max_deviation = 0.0

    print("\nComparisons to reference:")
    for i, result in enumerate(results[1:], 1):
        calc = result['calculated_raw']
        diff = max(abs(calc[j] - reference[j]) for j in range(3))
        max_deviation = max(max_deviation, diff)

        status = "✓ PASS" if diff < 0.05 else "✗ FAIL"
        if diff >= 0.05:
            all_passed = False

        print(f"\n{result['name']}")
        print(f"  Calculated: [{calc[0]:7.3f}, {calc[1]:7.3f}, {calc[2]:7.3f}] g")
        print(f"  Difference: {diff:.4f}g  {status}")

    # Also compare to actual reading at 0,0,0 (just for info)
    print(f"\n" + "-" * 70)
    print(f"Comparison to actual raw (at 0,0,0):")
    print(f"  Actual:     [{imu_actual_raw[0]:7.3f}, {imu_actual_raw[1]:7.3f}, {imu_actual_raw[2]:7.3f}] g")
    diff_to_actual = max(abs(reference[j] - imu_actual_raw[j]) for j in range(3))
    print(f"  Difference: {diff_to_actual:.4f}g")
    if diff_to_actual > 0.05:
        print(f"  Note: Board likely moved between readings (this is OK)")

    # Restore original alignment
    print(f"\n[RESTORE] Restoring original alignment...")
    if not set_board_alignment(ser, original_alignment['pitch'], original_alignment['roll'], original_alignment['yaw']):
        print("    WARNING: Set alignment failed")
    if not save_eeprom(ser):
        print("    WARNING: Save failed")
    print("    Rebooting...")
    reboot_fc(ser)
    ser.close()

    device = wait_for_fc_after_reboot(device)
    if device:
        print(f"    FC ready at {device}")

    # Final summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("  Inverse transformation works correctly for all orientations.")
        print("  The wizard can detect alignment without resetting to 0,0,0!")
    else:
        print("✗ SOME TESTS FAILED")
        print("  Inverse transformation needs debugging.")
    print("=" * 70)

if __name__ == '__main__':
    main()

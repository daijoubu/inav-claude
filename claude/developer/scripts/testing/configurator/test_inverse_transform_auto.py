#!/usr/bin/env python3
"""
Test inverse transformation to get raw sensor data from MSP_RAW_IMU
Automatically handles device reconnection after reboot
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
    print(f"  Waiting for FC to disconnect...")
    start = time.time()

    # Wait for original device to disappear (up to 5 seconds)
    while os.path.exists(original_device) and (time.time() - start) < 5:
        time.sleep(0.1)

    if os.path.exists(original_device):
        print(f"  WARNING: Device didn't disconnect, continuing anyway...")
    else:
        print(f"  Device disconnected")

    # Wait for any ttyACM device to appear
    print(f"  Waiting for FC to reconnect...")
    device = None
    while (time.time() - start) < timeout:
        device = find_fc_device()
        if device:
            break
        time.sleep(0.5)

    if device:
        time.sleep(2)  # Give it time to fully enumerate
        elapsed = time.time() - start
        print(f"  FC reconnected at {device} after {elapsed:.1f}s")
        return device
    else:
        print(f"  ERROR: FC did not reconnect within {timeout}s")
        return None

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
    # Read as unsigned, convert to signed
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
    if b'$M!' in response:
        return False
    return True

def save_eeprom(ser):
    """Save settings to EEPROM"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_EEPROM_WRITE))
    time.sleep(1.0)
    response = ser.read(64)
    if b'$M!' in response:
        return False
    return True

def reboot_fc(ser):
    """Reboot the FC via MSP"""
    ser.reset_input_buffer()
    ser.write(build_msp_request(MSP_REBOOT))
    time.sleep(0.1)
    # Don't wait for response, FC will disconnect
    return True

def build_rotation_matrix(roll_deg, pitch_deg, yaw_deg):
    """
    Build rotation matrix from Euler angles (ZYX order: yaw, pitch, roll)
    This matches INAV's coordinate system.
    """
    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)

    # Rotation matrix components
    cr = math.cos(roll)
    sr = math.sin(roll)
    cp = math.cos(pitch)
    sp = math.sin(pitch)
    cy = math.cos(yaw)
    sy = math.sin(yaw)

    # Combined rotation matrix R = Rz(yaw) * Ry(pitch) * Rx(roll)
    R = [
        [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
        [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
        [-sp,   cp*sr,            cp*cr           ]
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
    """Apply rotation matrix to a vector"""
    return [
        R[0][0]*vec[0] + R[0][1]*vec[1] + R[0][2]*vec[2],
        R[1][0]*vec[0] + R[1][1]*vec[1] + R[1][2]*vec[2],
        R[2][0]*vec[0] + R[2][1]*vec[1] + R[2][2]*vec[2]
    ]

def main():
    # Find FC device
    device = find_fc_device()
    if not device:
        print("ERROR: No FC device found (looking for /dev/ttyACM*)")
        sys.exit(1)

    baudrate = 115200
    print(f"Connecting to {device} at {baudrate}...")
    ser = serial.Serial(device, baudrate, timeout=1)
    time.sleep(0.5)
    print("Connected!\n")

    print("=" * 70)
    print("TEST: Inverse transformation to get raw sensor data")
    print("=" * 70)
    print("\n⚠️  CRITICAL: Place board FLAT on table and DO NOT TOUCH IT")
    print("    during the entire test. The board will reboot 3 times.")
    print("    Any movement will invalidate the test.\n")
    input("Press Enter when board is stable and you're ready...")

    # Step 1: Read and save original FC alignment
    print("\n[1] Reading current FC alignment...")
    original_alignment = read_board_alignment(ser)
    if not original_alignment:
        print("    ERROR: Failed to read alignment")
        sys.exit(1)
    print(f"    Original: roll={original_alignment['roll']:.1f}°, pitch={original_alignment['pitch']:.1f}°, yaw={original_alignment['yaw']:.1f}°")

    # Step 1b: Set FC to roll=90° for testing
    print("\n[1b] Setting FC to roll=90° for testing...")
    if not set_board_alignment(ser, 0, 90, 0):
        print("    WARNING: Set alignment failed")
        sys.exit(1)
    if not save_eeprom(ser):
        print("    WARNING: Save failed")
        sys.exit(1)

    print("    Rebooting FC to apply roll=90°...")
    reboot_fc(ser)
    ser.close()

    new_device = wait_for_fc_after_reboot(device)
    if not new_device:
        print("ERROR: FC did not reconnect")
        sys.exit(1)

    print(f"    Reconnecting to {new_device}...")
    device = new_device
    ser = serial.Serial(device, baudrate, timeout=1)
    time.sleep(1)

    # Verify it's set
    alignment = read_board_alignment(ser)
    if not alignment:
        print("    ERROR: Failed to read alignment after reboot")
        sys.exit(1)
    print(f"    Confirmed: roll={alignment['roll']:.1f}°, pitch={alignment['pitch']:.1f}°, yaw={alignment['yaw']:.1f}°")

    # Step 2: Read MSP_RAW_IMU with current alignment
    print("\n[2] Reading MSP_RAW_IMU (transformed data)...")
    print("    Keep board FLAT on table!")
    time.sleep(2)

    imu_transformed = read_raw_imu(ser)
    if not imu_transformed:
        print("    ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Transformed: [{imu_transformed[0]:7.3f}, {imu_transformed[1]:7.3f}, {imu_transformed[2]:7.3f}] g")

    # Step 3: Apply inverse transformation
    print("\n[3] Applying inverse transformation...")
    R = build_rotation_matrix(alignment['roll'], alignment['pitch'], alignment['yaw'])
    R_inv = transpose_matrix(R)  # Inverse = transpose for rotation matrices

    imu_raw = apply_rotation(R_inv, imu_transformed)
    print(f"    Raw sensor: [{imu_raw[0]:7.3f}, {imu_raw[1]:7.3f}, {imu_raw[2]:7.3f}] g")

    # Step 4: Set FC to 0,0,0 to verify
    print("\n[4] Setting FC to 0,0,0 and rebooting to verify...")
    if not set_board_alignment(ser, 0, 0, 0):
        print("    WARNING: Set alignment failed")
    if not save_eeprom(ser):
        print("    WARNING: Save failed")

    print("    Rebooting FC...")
    reboot_fc(ser)
    ser.close()

    # Wait for reconnection
    new_device = wait_for_fc_after_reboot(device)
    if not new_device:
        print("ERROR: FC did not reconnect")
        sys.exit(1)

    # Reconnect
    print(f"    Reconnecting to {new_device}...")
    ser = serial.Serial(new_device, baudrate, timeout=1)
    time.sleep(1)

    # Step 5: Read MSP_RAW_IMU with 0,0,0 (should match our calculated raw)
    print("\n[5] Reading MSP_RAW_IMU with FC at 0,0,0...")
    imu_actual_raw = read_raw_imu(ser)
    if not imu_actual_raw:
        print("    ERROR: Failed to read IMU")
        sys.exit(1)
    print(f"    Actual raw: [{imu_actual_raw[0]:7.3f}, {imu_actual_raw[1]:7.3f}, {imu_actual_raw[2]:7.3f}] g")

    # Sanity check: gravity magnitude should be ~1.0g
    mag_actual = math.sqrt(imu_actual_raw[0]**2 + imu_actual_raw[1]**2 + imu_actual_raw[2]**2)
    mag_calc = math.sqrt(imu_raw[0]**2 + imu_raw[1]**2 + imu_raw[2]**2)
    print(f"    Magnitude: actual={mag_actual:.3f}g, calculated={mag_calc:.3f}g")

    if mag_actual < 0.85 or mag_actual > 1.15:
        print(f"\n⚠️  WARNING: Board appears to have moved! Gravity magnitude is {mag_actual:.3f}g")
        print("    Expected ~1.0g. The board may have been disturbed during reboot.")
        print("    Test results may not be valid.")

    # Step 6: Compare
    print("\n" + "=" * 70)
    print("COMPARISON:")
    print("=" * 70)
    print(f"Calculated raw: [{imu_raw[0]:7.3f}, {imu_raw[1]:7.3f}, {imu_raw[2]:7.3f}] g")
    print(f"Actual raw:     [{imu_actual_raw[0]:7.3f}, {imu_actual_raw[1]:7.3f}, {imu_actual_raw[2]:7.3f}] g")

    diff = max(abs(imu_raw[i] - imu_actual_raw[i]) for i in range(3))
    print(f"\nMax difference: {diff:.4f} g")

    if diff < 0.01:
        print("\n✓ SUCCESS! Inverse transformation works correctly!")
        print("  The wizard can detect alignment without resetting to 0,0,0!")
    else:
        print("\n✗ MISMATCH - Inverse transformation has errors")
        print("  Need to debug the rotation matrix calculation")

    # Restore original alignment
    print(f"\n[6] Restoring original alignment: roll={original_alignment['roll']:.1f}°, pitch={original_alignment['pitch']:.1f}°, yaw={original_alignment['yaw']:.1f}°...")
    if not set_board_alignment(ser, original_alignment['pitch'], original_alignment['roll'], original_alignment['yaw']):
        print("    WARNING: Set alignment failed")
    if not save_eeprom(ser):
        print("    WARNING: Save failed")

    print("    Rebooting FC to apply restored alignment...")
    reboot_fc(ser)
    ser.close()

    new_device = wait_for_fc_after_reboot(new_device)
    if new_device:
        print(f"    FC ready at {new_device}")

    print("\nDone!")

if __name__ == '__main__':
    main()

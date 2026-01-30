#!/usr/bin/env python3
"""
Quick Auto Alignment Test

Simplified script to test board alignment detection.
Just reads two positions and calculates alignment.

Usage:
    python3 quick_alignment_test.py /dev/ttyACM1
"""

import serial
import struct
import time
import sys
import math

# MSP constants
MSP_HEADER = b'$M<'
MSP_RAW_IMU = 102
ACC_SCALE = 512.0


def calculate_checksum(size: int, cmd: int, data: bytes = b'') -> int:
    """Calculate MSPv1 checksum (XOR)"""
    checksum = size ^ cmd
    for byte in data:
        checksum ^= byte
    return checksum


def build_msp_request(cmd: int, data: bytes = b'') -> bytes:
    """Build MSPv1 request packet"""
    size = len(data)
    checksum = calculate_checksum(size, cmd, data)
    return MSP_HEADER + struct.pack('BB', size, cmd) + data + struct.pack('B', checksum)


def parse_msp_response(data: bytes):
    """Parse MSP response, return (cmd, payload) or None"""
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


def read_raw_imu(ser) -> dict:
    """Send MSP_RAW_IMU and parse response"""
    ser.reset_input_buffer()
    request = build_msp_request(MSP_RAW_IMU)
    ser.write(request)
    time.sleep(0.02)
    response = ser.read(64)

    result = parse_msp_response(response)
    if result is None:
        return None

    cmd, payload = result
    if cmd != MSP_RAW_IMU or len(payload) < 18:
        return None

    values = struct.unpack('<hhhhhhhhh', payload[:18])

    return {
        'acc': [values[0] / ACC_SCALE, values[1] / ACC_SCALE, values[2] / ACC_SCALE],
        'gyro': [values[3], values[4], values[5]],
        'mag': [values[6], values[7], values[8]]
    }


def calculate_pitch_roll(acc):
    """Calculate pitch and roll from accelerometer (in degrees)"""
    pitch = math.atan2(acc[0], math.sqrt(acc[1]**2 + acc[2]**2)) * 180 / math.pi
    roll = math.atan2(-acc[1], acc[2]) * 180 / math.pi
    return pitch, roll


def calculate_yaw(delta_pitch, delta_roll, upside_down):
    """Calculate yaw from delta pitch/roll using atan2"""
    yaw = math.atan2(-delta_roll, delta_pitch) * 180 / math.pi

    if upside_down:
        yaw = yaw + 180

    # Normalize to 0-360
    yaw = ((yaw % 360) + 360) % 360

    # Detect corner mount
    corner_mount = (abs(delta_pitch) > 15 and abs(delta_roll) > 15 and
                    abs(delta_pitch) < 35 and abs(delta_roll) < 35)

    # Snap to nearest 45° or 90°
    snap = 45 if corner_mount else 90
    yaw = round(yaw / snap) * snap

    return int(yaw % 360)


def average_readings(ser, count=10):
    """Average multiple IMU readings"""
    readings = []
    for _ in range(count):
        data = read_raw_imu(ser)
        if data:
            readings.append(data)
        time.sleep(0.01)

    if not readings:
        return None

    avg = {
        'acc': [
            sum(r['acc'][0] for r in readings) / len(readings),
            sum(r['acc'][1] for r in readings) / len(readings),
            sum(r['acc'][2] for r in readings) / len(readings)
        ]
    }
    return avg


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quick_alignment_test.py <port> [baudrate]")
        print("Example: python3 quick_alignment_test.py /dev/ttyACM0")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    print(f"Connecting to {port} at {baudrate} baud...")
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    print("Connected!\n")

    print("=" * 60)
    print("QUICK AUTO ALIGNMENT TEST")
    print("=" * 60)
    print("\nThis will test the board alignment detection algorithm.")
    print("It reads two positions and calculates the alignment.\n")

    # Step 1: Flat reading
    print("STEP 1: FLAT POSITION")
    print("-" * 60)
    print("Place the FC flat on the table (level).")
    print("Press Enter when ready...")
    input()

    print("Reading sensors...")
    flat_reading = average_readings(ser, count=10)
    if not flat_reading:
        print("ERROR: Failed to read sensor data")
        ser.close()
        sys.exit(1)

    pitch_flat, roll_flat = calculate_pitch_roll(flat_reading['acc'])
    upside_down = abs(roll_flat) > 90

    print(f"✓ Flat reading:")
    print(f"  Accelerometer: [{flat_reading['acc'][0]:.3f}, {flat_reading['acc'][1]:.3f}, {flat_reading['acc'][2]:.3f}] g")
    print(f"  Pitch: {pitch_flat:.1f}°")
    print(f"  Roll: {roll_flat:.1f}°")
    print(f"  Upside down: {upside_down}")

    # Step 2: Tilted reading
    print("\nSTEP 2: NOSE UP POSITION")
    print("-" * 60)
    print("Now tilt the FC NOSE UP by about 45°.")
    print("(Doesn't need to be exact - anywhere 30-60° is fine)")
    print("Press Enter when ready...")
    input()

    print("Reading sensors...")
    tilted_reading = average_readings(ser, count=10)
    if not tilted_reading:
        print("ERROR: Failed to read sensor data")
        ser.close()
        sys.exit(1)

    pitch_tilted, roll_tilted = calculate_pitch_roll(tilted_reading['acc'])

    print(f"✓ Tilted reading:")
    print(f"  Accelerometer: [{tilted_reading['acc'][0]:.3f}, {tilted_reading['acc'][1]:.3f}, {tilted_reading['acc'][2]:.3f}] g")
    print(f"  Pitch: {pitch_tilted:.1f}°")
    print(f"  Roll: {roll_tilted:.1f}°")

    # Step 3: Calculate alignment
    print("\nSTEP 3: CALCULATING ALIGNMENT")
    print("-" * 60)

    delta_pitch = pitch_tilted - pitch_flat
    delta_roll = roll_tilted - roll_flat

    # Normalize deltas to [-180, 180]
    if delta_pitch > 180: delta_pitch -= 360
    elif delta_pitch < -180: delta_pitch += 360
    if delta_roll > 180: delta_roll -= 360
    elif delta_roll < -180: delta_roll += 360

    print(f"Delta pitch: {delta_pitch:.1f}°")
    print(f"Delta roll: {delta_roll:.1f}°")

    detected_yaw = calculate_yaw(delta_pitch, delta_roll, upside_down)
    detected_pitch = round(pitch_flat)
    detected_roll = round(roll_flat)

    print(f"\n{'=' * 60}")
    print("DETECTED BOARD ALIGNMENT:")
    print(f"{'=' * 60}")
    print(f"  align_board_pitch = {detected_pitch}")
    print(f"  align_board_roll  = {detected_roll}")
    print(f"  align_board_yaw   = {detected_yaw}")
    print(f"{'=' * 60}")

    print("\nInterpretation:")
    if detected_yaw == 0:
        print("  → FC arrow is pointing FORWARD")
    elif detected_yaw == 90:
        print("  → FC arrow is pointing RIGHT (90° CW)")
    elif detected_yaw == 180:
        print("  → FC arrow is pointing BACKWARD (180°)")
    elif detected_yaw == 270:
        print("  → FC arrow is pointing LEFT (270° CCW / 90° CCW)")
    elif detected_yaw == 45:
        print("  → FC arrow is pointing 45° (corner mount)")
    else:
        print(f"  → FC arrow is pointing {detected_yaw}°")

    if upside_down:
        print("  → FC is UPSIDE DOWN")

    print("\nTest another orientation? (y/n): ", end='')
    response = input().strip().lower()
    if response == 'y':
        print("\n\n")
        main()
    else:
        ser.close()
        print("\nDone!")


if __name__ == '__main__':
    main()

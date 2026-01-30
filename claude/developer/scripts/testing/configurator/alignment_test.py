#!/usr/bin/env python3
"""
Auto Alignment Test Tool

Reads sensor data from FC and calculates board + compass alignment values
using the same math as the Configurator's Auto Align wizard (magnetometer.js).

Usage:
    python3 alignment_test.py /dev/ttyACM0              # Run all tests
    python3 alignment_test.py /dev/ttyACM0 115200       # Custom baud rate
    python3 alignment_test.py /dev/ttyACM0 115200 6 7 8 # Run tests 6, 7, 8 only

The script guides you through each step automatically.
"""

import serial
import struct
import time
import sys
import math
import os

# MSP constants
MSP_HEADER = b'$M<'
MSP_RAW_IMU = 102
MSP_ATTITUDE = 108
MSP_CALIBRATION_DATA = 14
MSP_BOARD_ALIGNMENT = 38
MSP_SET_BOARD_ALIGNMENT = 39
MSP_EEPROM_WRITE = 250

# Accelerometer scale factor (raw to g)
# INAV uses 512 as divisor for most sensors
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

    # Find header
    idx = data.find(b'$M>')
    if idx < 0:
        idx = data.find(b'$M!')  # Error response
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
    # Clear any pending data
    ser.reset_input_buffer()

    # Send request
    request = build_msp_request(MSP_RAW_IMU)
    ser.write(request)

    # Read response (expect ~24 bytes: header + size + cmd + 18 bytes data + checksum)
    time.sleep(0.02)
    response = ser.read(64)

    result = parse_msp_response(response)
    if result is None:
        return None

    cmd, payload = result
    if cmd != MSP_RAW_IMU or len(payload) < 18:
        return None

    # Parse 9 int16 values: acc[3], gyro[3], mag[3]
    values = struct.unpack('<hhhhhhhhh', payload[:18])

    return {
        'acc': [values[0] / ACC_SCALE, values[1] / ACC_SCALE, values[2] / ACC_SCALE],
        'gyro': values[3:6],
        'mag': values[6:9]
    }


def read_attitude(ser) -> dict:
    """Send MSP_ATTITUDE and parse response"""
    ser.reset_input_buffer()

    request = build_msp_request(MSP_ATTITUDE)
    ser.write(request)

    time.sleep(0.02)
    response = ser.read(64)

    result = parse_msp_response(response)
    if result is None:
        return None

    cmd, payload = result
    if cmd != MSP_ATTITUDE or len(payload) < 6:
        return None

    # Parse: roll (decidegrees), pitch (decidegrees), yaw/heading (degrees)
    roll, pitch, heading = struct.unpack('<hhh', payload[:6])

    return {
        'roll': roll / 10.0,
        'pitch': pitch / 10.0,
        'heading': heading
    }


def read_board_alignment(ser) -> dict:
    """Read current board alignment from FC"""
    ser.reset_input_buffer()
    request = build_msp_request(MSP_BOARD_ALIGNMENT)
    ser.write(request)
    time.sleep(0.05)
    response = ser.read(64)

    result = parse_msp_response(response)
    if result is None:
        return None

    cmd, payload = result
    if cmd != MSP_BOARD_ALIGNMENT or len(payload) < 6:
        return None

    # Parse: roll, pitch, yaw in decidegrees
    roll, pitch, yaw = struct.unpack('<hhh', payload[:6])

    return {
        'pitch': pitch // 10,
        'roll': roll // 10,
        'yaw': yaw // 10
    }


def set_board_alignment(ser, pitch, roll, yaw) -> bool:
    """Set board alignment on FC (decidegrees)"""
    ser.reset_input_buffer()
    # Pack as roll, pitch, yaw in decidegrees
    data = struct.pack('<hhh', roll * 10, pitch * 10, yaw * 10)
    request = build_msp_request(MSP_SET_BOARD_ALIGNMENT, data)
    ser.write(request)
    time.sleep(0.05)
    response = ser.read(64)
    result = parse_msp_response(response)
    return result is not None


def save_settings(ser) -> bool:
    """Save settings to EEPROM (may cause reboot)"""
    ser.reset_input_buffer()
    request = build_msp_request(MSP_EEPROM_WRITE)
    ser.write(request)
    time.sleep(0.1)
    response = ser.read(64)
    return True  # May not get response if FC reboots


def wait_for_fc(ser, port, baudrate, timeout=5) -> bool:
    """Wait for FC to respond after potential reboot"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            ser.reset_input_buffer()
            request = build_msp_request(MSP_BOARD_ALIGNMENT)
            ser.write(request)
            time.sleep(0.1)
            response = ser.read(64)
            if parse_msp_response(response):
                return True
        except:
            pass
        time.sleep(0.2)
    return False


def calculate_pitch_roll(acc):
    """Calculate pitch and roll from accelerometer (in degrees)"""
    # Standard aerospace convention: nose up = positive pitch, right wing down = positive roll
    pitch = math.atan2(acc[0], math.sqrt(acc[1]**2 + acc[2]**2)) * 180 / math.pi
    roll = math.atan2(-acc[1], acc[2]) * 180 / math.pi
    return pitch, roll


def calculate_yaw(delta_pitch, delta_roll, upside_down=False):
    """Calculate board yaw from pitch/roll deltas

    When tilting aircraft nose up:
    - Sensor at 0° (forward): delta_pitch increases, delta_roll ~0 → yaw = 0°
    - Sensor at 90° (right): delta_pitch ~0, delta_roll increases → yaw = 90°
    - Sensor at 180° (back): delta_pitch decreases, delta_roll ~0 → yaw = 180°
    - Sensor at 270° (left): delta_pitch ~0, delta_roll decreases → yaw = 270°

    Uses atan2(delta_roll, delta_pitch) to determine the sensor orientation.
    """
    yaw = math.atan2(delta_roll, delta_pitch) * 180 / math.pi

    # upside_down parameter kept for API compatibility but not used

    # Normalize to 0-360
    yaw = ((yaw % 360) + 360) % 360

    # Snap to nearest 45° or 90°
    corner_mount = (abs(delta_pitch) > 15 and abs(delta_roll) > 15 and
                   abs(delta_pitch) < 35 and abs(delta_roll) < 35)
    snap = 45 if corner_mount else 90
    yaw = round(yaw / snap) * snap

    return yaw % 360


def analyze_compass_heading(heading_flat, heading_east):
    """Analyze compass heading test results.

    Returns correction values for compass alignment.
    """
    # Heading change when turning 90° to the right (N→E)
    change = (heading_east - heading_flat + 360) % 360
    change_snapped = round(change / 90) * 90

    # If 90° physical turn caused 270° heading change, compass is upside-down
    upside_down = change_snapped > 180
    roll_correction = 180 if upside_down else 0

    # How much yaw correction is needed?
    # When pointing East, heading should be 90°
    raw_yaw_correction = (90 - heading_east + 360) % 360
    if raw_yaw_correction > 180:
        raw_yaw_correction -= 360

    # Snap to 45° or 90°
    use45 = (abs(heading_flat % 45) < 15) and (abs(raw_yaw_correction % 45) < 15)
    if use45:
        yaw_correction = round(raw_yaw_correction / 45) * 45
    else:
        yaw_correction = round(raw_yaw_correction / 90) * 90
    yaw_correction = ((yaw_correction % 360) + 360) % 360

    return {
        'heading_change': change,
        'heading_change_snapped': change_snapped,
        'upside_down': upside_down,
        'roll_correction': roll_correction,
        'yaw_correction': yaw_correction
    }


def calculate_compass_alignment(old_compass, delta_board, compass_correction):
    """Calculate new compass alignment.

    Formula: new_compass = old_compass - delta_board + compass_correction
    """
    new_pitch = old_compass['pitch'] - delta_board['pitch']
    new_roll = old_compass['roll'] - delta_board['roll'] + compass_correction['roll']
    new_yaw = old_compass['yaw'] - delta_board['yaw'] + compass_correction['yaw']

    # Normalize
    new_pitch = ((new_pitch % 360) + 360) % 360
    if new_pitch > 180:
        new_pitch -= 360

    new_roll = ((new_roll % 360) + 360) % 360
    if new_roll > 180:
        new_roll -= 360

    new_yaw = ((new_yaw % 360) + 360) % 360

    return {'pitch': round(new_pitch), 'roll': round(new_roll), 'yaw': round(new_yaw)}


def print_imu_data(imu, label=""):
    """Pretty print IMU data"""
    acc = imu['acc']
    mag = acc[0]**2 + acc[1]**2 + acc[2]**2
    magnitude = math.sqrt(mag)
    pitch, roll = calculate_pitch_roll(acc)

    print(f"\n{label}")
    print(f"  Accelerometer (g): [{acc[0]:7.3f}, {acc[1]:7.3f}, {acc[2]:7.3f}]")
    print(f"  Magnitude: {magnitude:.3f} (should be ~1.0)")
    print(f"  Pitch: {pitch:6.1f}°  (nose up = positive)")
    print(f"  Roll:  {roll:6.1f}°  (right wing down = positive)")

    return pitch, roll


def average_readings(ser, count=10, delay=0.05):
    """Take multiple readings and average them."""
    imu_readings = []
    att_readings = []

    for _ in range(count):
        imu = read_raw_imu(ser)
        att = read_attitude(ser)
        if imu:
            imu_readings.append(imu)
        if att:
            att_readings.append(att)
        time.sleep(delay)

    if not imu_readings:
        return None

    # Average accelerometer
    avg_acc = [
        sum(r['acc'][0] for r in imu_readings) / len(imu_readings),
        sum(r['acc'][1] for r in imu_readings) / len(imu_readings),
        sum(r['acc'][2] for r in imu_readings) / len(imu_readings)
    ]

    # Average magnetometer
    avg_mag = [
        sum(r['mag'][0] for r in imu_readings) / len(imu_readings),
        sum(r['mag'][1] for r in imu_readings) / len(imu_readings),
        sum(r['mag'][2] for r in imu_readings) / len(imu_readings)
    ]

    # Average heading
    avg_heading = None
    if att_readings:
        avg_heading = sum(r['heading'] for r in att_readings) / len(att_readings)

    return {'acc': avg_acc, 'mag': avg_mag, 'heading': avg_heading}


def describe_orientation(pitch, roll, yaw):
    """Return human-readable description of board orientation."""
    parts = []

    # Yaw description
    yaw_normalized = yaw % 360
    if yaw_normalized == 0:
        parts.append("arrow FORWARD")
    elif yaw_normalized == 90:
        parts.append("arrow RIGHT")
    elif yaw_normalized == 180:
        parts.append("arrow BACKWARD")
    elif yaw_normalized == 270:
        parts.append("arrow LEFT")
    else:
        parts.append(f"yaw {yaw_normalized}°")

    # Roll description (upside-down)
    if abs(roll) == 180:
        parts.append("UPSIDE-DOWN")
    elif roll != 0:
        parts.append(f"roll {roll}°")

    # Pitch description
    if pitch != 0:
        parts.append(f"pitch {pitch}°")

    return ", ".join(parts)


def run_single_test(ser, fc_setting, physical_orientation):
    """
    Run a single alignment test.

    fc_setting: The alignment currently set on FC
    physical_orientation: How the user should physically orient the board

    Returns: (result_dict, pass_bool)
    """
    desc = describe_orientation(
        physical_orientation['pitch'],
        physical_orientation['roll'],
        physical_orientation['yaw']
    )

    print(f"\n  Orient board: {desc}")
    print(f"  (FC setting: pitch={fc_setting['pitch']}, roll={fc_setting['roll']}, yaw={fc_setting['yaw']})")
    input("  Press Enter when ready...")

    # Flat reading
    flat_reading = average_readings(ser, count=10)
    if not flat_reading:
        print("  ERROR: Failed to read sensor data")
        return None, False

    pitch_flat, roll_flat = calculate_pitch_roll(flat_reading['acc'])
    upside_down = abs(roll_flat) > 90
    print(f"  Flat: pitch={pitch_flat:.1f}°, roll={roll_flat:.1f}°, upside_down={upside_down}")

    # Tilted reading
    print("  Now tilt NOSE UP ~45°...")
    input("  Press Enter when ready...")

    tilted_reading = average_readings(ser, count=10)
    if not tilted_reading:
        print("  ERROR: Failed to read sensor data")
        return None, False

    pitch_tilted, roll_tilted = calculate_pitch_roll(tilted_reading['acc'])
    print(f"  Tilted: pitch={pitch_tilted:.1f}°, roll={roll_tilted:.1f}°")

    # Calculate
    delta_pitch = pitch_tilted - pitch_flat
    delta_roll = roll_tilted - roll_flat

    # Normalize deltas to [-180, 180]
    if delta_pitch > 180: delta_pitch -= 360
    elif delta_pitch < -180: delta_pitch += 360
    if delta_roll > 180: delta_roll -= 360
    elif delta_roll < -180: delta_roll += 360

    detected_yaw = calculate_yaw(delta_pitch, delta_roll, upside_down)
    pitch_offset = round(pitch_flat / 45) * 45
    roll_offset = round(roll_flat / 45) * 45

    # MSP_RAW_IMU provides raw sensor data (not transformed by FC board alignment)
    # Therefore detected values are absolute sensor orientations
    # They do NOT need adjustment for existing FC settings
    new_pitch = pitch_offset
    new_roll = roll_offset
    new_yaw = detected_yaw

    # Normalize to [-180, 180] for pitch/roll, [0, 360) for yaw
    if new_pitch > 180: new_pitch -= 360
    if new_roll > 180: new_roll -= 360

    result = {'pitch': int(new_pitch), 'roll': int(new_roll), 'yaw': int(new_yaw)}

    # Expected: result should match physical orientation
    exp_pitch = physical_orientation['pitch']
    exp_roll = physical_orientation['roll']
    exp_yaw = physical_orientation['yaw'] % 360
    if exp_pitch > 180: exp_pitch -= 360
    if exp_roll > 180: exp_roll -= 360

    expected = {'pitch': exp_pitch, 'roll': exp_roll, 'yaw': exp_yaw}

    # Compare with tolerance for ±180° equivalence
    def angles_equal(a, b):
        diff = abs(a - b)
        return diff == 0 or diff == 360

    passed = (angles_equal(result['pitch'], expected['pitch']) and
              angles_equal(result['roll'], expected['roll']) and
              angles_equal(result['yaw'], expected['yaw']))

    print(f"  Result: pitch={result['pitch']}, roll={result['roll']}, yaw={result['yaw']}")
    print(f"  Expected: pitch={expected['pitch']}, roll={expected['roll']}, yaw={expected['yaw']}")
    print(f"  {'PASS' if passed else 'FAIL'}")

    return result, passed


def run_test_suite(ser, port, baudrate, test_numbers=None):
    """Run comprehensive test suite with various FC settings and physical orientations.

    Args:
        ser: Serial connection
        port: Port name
        baudrate: Baud rate
        test_numbers: List of test numbers to run (1-8), or None for all tests
    """

    # Test matrix: (fc_setting, physical_orientation)
    # When FC setting matches physical orientation, result should equal both
    tests = [
        # FC at 0,0,0 - test various physical orientations
        ({'pitch': 0, 'roll': 0, 'yaw': 0}, {'pitch': 0, 'roll': 0, 'yaw': 0}),      # Test 1
        ({'pitch': 0, 'roll': 0, 'yaw': 0}, {'pitch': 0, 'roll': 0, 'yaw': 90}),     # Test 2
        ({'pitch': 0, 'roll': 0, 'yaw': 0}, {'pitch': 0, 'roll': 0, 'yaw': 180}),    # Test 3
        ({'pitch': 0, 'roll': 0, 'yaw': 0}, {'pitch': 0, 'roll': 0, 'yaw': 270}),    # Test 4
        ({'pitch': 0, 'roll': 0, 'yaw': 0}, {'pitch': 0, 'roll': 180, 'yaw': 0}),    # Test 5

        # FC at yaw=90 - physical should match for identity test
        ({'pitch': 0, 'roll': 0, 'yaw': 90}, {'pitch': 0, 'roll': 0, 'yaw': 90}),    # Test 6

        # FC at yaw=90, physical at yaw=0 - should calculate yaw=0
        ({'pitch': 0, 'roll': 0, 'yaw': 90}, {'pitch': 0, 'roll': 0, 'yaw': 0}),     # Test 7

        # FC upside-down, physical upside-down - identity
        ({'pitch': 0, 'roll': 180, 'yaw': 0}, {'pitch': 0, 'roll': 180, 'yaw': 0}),  # Test 8
    ]

    # Filter tests if specific test numbers requested
    if test_numbers:
        selected_tests = [(i, tests[i-1]) for i in test_numbers if 1 <= i <= len(tests)]
        if not selected_tests:
            print(f"ERROR: Invalid test numbers. Valid range: 1-{len(tests)}")
            return
        print("\n" + "=" * 60)
        print(f"RUNNING SELECTED TESTS: {test_numbers}")
        print("=" * 60)
    else:
        selected_tests = [(i+1, tests[i]) for i in range(len(tests))]
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"\nRunning all {len(tests)} tests...")

    print("For each test, orient the board as instructed.\n")

    results = []
    current_fc_setting = None

    for test_num, (fc_setting, physical) in selected_tests:
        print(f"\n{'='*60}")
        print(f"TEST {test_num}/{len(tests)}")

        # Set FC alignment if different from current
        if fc_setting != current_fc_setting:
            print(f"\nSetting FC alignment: {fc_setting}")
            if set_board_alignment(ser, fc_setting['pitch'], fc_setting['roll'], fc_setting['yaw']):
                save_settings(ser)
                print("  Saving...")
                time.sleep(1)
                if wait_for_fc(ser, port, baudrate, timeout=5):
                    current_fc_setting = read_board_alignment(ser)
                    if current_fc_setting:
                        print(f"  Confirmed: {current_fc_setting}")
                    else:
                        current_fc_setting = fc_setting.copy()
                else:
                    print("  WARNING: FC not responding")
                    current_fc_setting = fc_setting.copy()
            else:
                print("  ERROR: Failed to set alignment")
                continue

        # Use current_fc_setting (actual FC value) not fc_setting (test parameter)
        result, passed = run_single_test(ser, current_fc_setting, physical)
        results.append((current_fc_setting, physical, result, passed))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, _, _, p in results if p)
    print(f"\nPassed: {passed_count}/{len(results)}")

    if passed_count < len(results):
        print("\nFailed tests:")
        for fc, phys, result, passed in results:
            if not passed:
                print(f"  FC={fc}, Physical={phys}")
                print(f"    Got: {result}")

    # Reset FC to 0,0,0
    print("\nResetting FC to 0,0,0...")
    set_board_alignment(ser, 0, 0, 0)
    save_settings(ser)
    time.sleep(1)
    wait_for_fc(ser, port, baudrate, timeout=5)
    print("Done.")

    return passed_count == len(results)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 alignment_test.py <port> [baudrate] [test_numbers...]")
        print("Example: python3 alignment_test.py /dev/ttyACM0")
        print("Example: python3 alignment_test.py /dev/ttyACM0 115200")
        print("Example: python3 alignment_test.py /dev/ttyACM0 115200 6 7 8")
        print("Example: python3 alignment_test.py /dev/ttyACM0 6 7 8  # Uses default 115200 baud")
        sys.exit(1)

    port = sys.argv[1]

    # Smart parsing: if argv[2] looks like a test number (< 100), treat as test number
    # Otherwise treat as baudrate
    if len(sys.argv) > 2:
        try:
            second_arg = int(sys.argv[2])
            if second_arg < 100:  # Likely a test number, not a baudrate
                baudrate = 115200
                test_arg_start = 2
            else:  # Likely a baudrate
                baudrate = second_arg
                test_arg_start = 3
        except ValueError:
            print("ERROR: Second argument must be a number (baudrate or test number)")
            sys.exit(1)
    else:
        baudrate = 115200
        test_arg_start = 2

    print(f"Connecting to {port} at {baudrate} baud...")

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(0.5)
        ser.reset_input_buffer()
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    # Read current settings from FC
    saved_board = read_board_alignment(ser)
    if saved_board:
        print(f"FC board alignment: {saved_board}")
    else:
        print("Could not read FC settings")

    print("\n" + "=" * 60)
    print("AUTO ALIGNMENT TEST TOOL")
    print("=" * 60)
    print("\nThis tool tests the board alignment detection algorithm.")
    print("It will guide you through orienting the board and verify")
    print("that the calculated alignment matches expectations.\n")

    # Parse test numbers from command line (determined by test_arg_start from above)
    test_numbers = None
    if len(sys.argv) > test_arg_start:
        try:
            test_numbers = [int(arg) for arg in sys.argv[test_arg_start:]]
            print(f"Will run tests: {test_numbers}")
        except ValueError:
            print("ERROR: Test numbers must be integers")
            print("Usage: python3 alignment_test.py <port> [baudrate] [test1] [test2] ...")
            sys.exit(1)

    cmd = input("Press Enter to start test suite (or 'q' to quit): ").strip().lower()

    if cmd != 'q':
        run_test_suite(ser, port, baudrate, test_numbers)

    ser.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()

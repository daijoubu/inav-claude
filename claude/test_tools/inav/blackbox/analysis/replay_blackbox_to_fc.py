#!/usr/bin/env python3
"""
Replay Blackbox Sensor Data to Flight Controller (SITL or HITL)

Replays GPS + IMU (accel, gyro, baro, mag) data from blackbox logs to a flight
controller via MSP_SIMULATOR (HITL mode). Works with both:
- SITL (Software In The Loop): tcp:localhost:5761
- HITL (Hardware In The Loop): /dev/ttyACM0 or similar serial port

This is useful for:
- Reproducing navigation issues in controlled environment
- Testing position estimator behavior with real flight data
- Debugging GPS/EPH oscillation issues
- Validating firmware changes against real flight data

FIRMWARE MODIFICATION REQUIRED:
This tool now sends real GPS EPH and EPV values from blackbox data.
Stock INAV firmware hardcodes EPH=100cm, EPV=100cm and ignores these values.
You must use MODIFIED INAV firmware that reads EPH/EPV from MSP_SIMULATOR packet.

Modification details:
- File: inav/src/main/fc/fc_msp.c
- Changes: Lines 4233-4260 modified to read EPH/EPV instead of hardcoding
- Build modified SITL: cd inav/build_sitl && cmake -DSITL=ON .. && make

Usage:
    # Replay to SITL (with modified firmware)
    python3 replay_blackbox_to_fc.py \\
        --csv blackbox.01.csv \\
        --port tcp:localhost:5761

    # Replay to physical FC (HITL, with modified firmware)
    python3 replay_blackbox_to_fc.py \\
        --csv blackbox.01.csv \\
        --port /dev/ttyACM0

    # Replay specific time range at 2x speed
    python3 replay_blackbox_to_fc.py \\
        --csv blackbox.01.csv \\
        --port tcp:localhost:5761 \\
        --start-time 11.0 \\
        --duration 10.0 \\
        --speed 2.0

Requirements:
    pip install mspapi2

Author: Claude Code
Date: 2026-01-01
"""

import sys
import time
import argparse
import csv
import struct
from pathlib import Path

# Add mspapi2 to path
import os
project_root = Path(__file__).resolve().parents[3]  # Up to inavflight/
mspapi2_path = project_root / 'mspapi2'
if mspapi2_path.exists():
    sys.path.insert(0, str(mspapi2_path))

try:
    from mspapi2 import MSPApi, InavMSP
except ImportError:
    print("ERROR: mspapi2 not found. Install with: pip install mspapi2")
    print(f"Or install from: {project_root}/mspapi2")
    sys.exit(1)


def send_msp_simulator(api: MSPApi, row: dict, has_gps: bool = False):
    """
    Send sensor data via MSP_SIMULATOR (0x201F).

    This is the HITL (Hardware In The Loop) command that sends all sensor data.

    Message format (all little-endian):
    - Flags (uint16): HITL_ENABLE (0x0001), HITL_HAS_NEW_GPS_DATA (0x0002)
    - GPS data (if HITL_HAS_NEW_GPS_DATA flag set):
        - fixType (uint8), numSat (uint8)
        - lat/lon (int32 × 10^7), altitude (uint32 cm)
        - speed (uint16 cm/s), course (uint16 decideg)
        - velNED (3× int16 cm/s)
        - EPH, EPV (2× uint16 cm) **NEW - requires modified firmware**
    - Attitude: roll, pitch, yaw (3× uint16 decideg) - set to 0 to let FC calculate
    - Accelerometer: X, Y, Z (3× int16 milli-G, firmware divides by 1000)
    - Gyro: X, Y, Z (3× int16 deg/s × 16, firmware divides by 16)
    - Barometer: pressure (uint32 Pa)
    - Magnetometer: X, Y, Z (3× int16, firmware divides by 20)

    FIRMWARE MODIFICATION REQUIRED:
    Stock INAV hardcodes GPS EPH=100cm and EPV=100cm in fc_msp.c:4233-4234.
    This tool now sends real EPH/EPV values, but requires modified firmware to read them.
    See: inav/src/main/fc/fc_msp.c (modified to read EPH/EPV from packet)

    See firmware: fc_msp.c:4160-4290
    """

    msg = bytearray()

    # Version (uint8) - MSP_SIMULATOR version
    # IMPORTANT: Must match firmware's SIMULATOR_MSP_VERSION in runtime_config.h
    SIMULATOR_MSP_VERSION = 2
    msg.append(SIMULATOR_MSP_VERSION)

    # Flags (uint8) - NOT uint16!
    # See firmware runtime_config.h for flag definitions
    flags = 0x01  # HITL_ENABLE = (1 << 0)
    if has_gps and 'GPS_fixType' in row and int(row.get('GPS_fixType', 0)) > 0:
        flags |= 0x10  # HITL_HAS_NEW_GPS_DATA = (1 << 4)
    msg.append(flags)

    # GPS data (if available)
    if flags & 0x0010:  # HITL_HAS_NEW_GPS_DATA
        try:
            # GPS fix type (uint8)
            msg.append(int(row['GPS_fixType']))
            # Satellites (uint8)
            msg.append(int(row['GPS_numSat']))
            # Latitude (int32, degrees × 10^7)
            lat_e7 = int(float(row['GPS_coord[0]']) * 1e7)
            msg.extend(struct.pack('<i', lat_e7))
            # Longitude (int32, degrees × 10^7)
            lon_e7 = int(float(row['GPS_coord[1]']) * 1e7)
            msg.extend(struct.pack('<i', lon_e7))
            # Altitude (uint32, cm)
            alt_cm = int(float(row['GPS_altitude']))
            msg.extend(struct.pack('<I', alt_cm))
            # Speed (uint16, cm/s)
            speed_cms = int(float(row['GPS_speed (m/s)']) * 100)
            msg.extend(struct.pack('<H', speed_cms))
            # Ground course (uint16, decidegrees)
            course = int(float(row['GPS_ground_course']))
            msg.extend(struct.pack('<H', course))
            # Velocity NED (3× int16, cm/s)
            vel_n = int(float(row['GPS_velned[0]']))
            vel_e = int(float(row['GPS_velned[1]']))
            vel_d = int(float(row['GPS_velned[2]']))
            msg.extend(struct.pack('<hhh', vel_n, vel_e, vel_d))

            # EPH and EPV (2× uint16, cm)
            # CRITICAL: These values are now sent to firmware (requires modified INAV)
            # Stock INAV hardcodes EPH=100, EPV=100 in fc_msp.c:4233-4234
            # Modified INAV reads these values from the packet
            eph_cm = int(float(row.get('GPS_eph', 100)))  # Default 100 cm if not present
            epv_cm = int(float(row.get('GPS_epv', 100)))  # Default 100 cm if not present
            msg.extend(struct.pack('<HH', eph_cm, epv_cm))
        except (KeyError, ValueError) as e:
            # GPS data incomplete, send without GPS flag
            print(f"Warning: Incomplete GPS data, skipping GPS for this sample: {e}")
            # Rebuild message without GPS flag
            msg = bytearray()
            msg.extend(struct.pack('<H', 0x0001))  # Only HITL_ENABLE

    # Attitude (roll, pitch, yaw) - 3× uint16 (decidegrees)
    # Set to 0 to let FC calculate from IMU data
    roll = 0
    pitch = 0
    yaw = 0
    msg.extend(struct.pack('<HHH', roll, pitch, yaw))

    # Accelerometer (X, Y, Z) - 3× int16 (milli-G)
    # accSmooth is in units of 1/512 G, convert to milli-G (G × 1000)
    # Firmware divides by 1000.0 to get G units (fc_msp.c:4254)
    try:
        acc_x = int(float(row['accSmooth[0]']) / 512.0 * 1000.0)
        acc_y = int(float(row['accSmooth[1]']) / 512.0 * 1000.0)
        acc_z = int(float(row['accSmooth[2]']) / 512.0 * 1000.0)
    except (KeyError, ValueError):
        # Fallback: 1G on Z axis (stationary)
        acc_x, acc_y, acc_z = 0, 0, 1000
    msg.extend(struct.pack('<hhh', acc_x, acc_y, acc_z))

    # Gyro (X, Y, Z) - 3× int16 (deg/s × 16)
    # gyroADC is already in deg/s × 16 format
    try:
        gyro_x = int(float(row['gyroADC[0]']))
        gyro_y = int(float(row['gyroADC[1]']))
        gyro_z = int(float(row['gyroADC[2]']))
    except (KeyError, ValueError):
        gyro_x, gyro_y, gyro_z = 0, 0, 0
    msg.extend(struct.pack('<hhh', gyro_x, gyro_y, gyro_z))

    # Barometer pressure (uint32 Pa)
    # BaroAlt is altitude in cm, convert to pressure
    # Rough approximation: P ≈ 101325 - altitude_m × 12 Pa
    try:
        baro_alt_cm = float(row['BaroAlt (cm)'])
        baro_pressure = int(101325 - (baro_alt_cm / 100.0) * 12)
    except (KeyError, ValueError):
        baro_pressure = 101325  # Sea level
    msg.extend(struct.pack('<I', baro_pressure))

    # Magnetometer (X, Y, Z) - 3× int16
    # Firmware divides by 20 (fc_msp.c:4265)
    try:
        mag_x = int(float(row['magADC[0]']) * 20)
        mag_y = int(float(row['magADC[1]']) * 20)
        mag_z = int(float(row['magADC[2]']) * 20)
    except (KeyError, ValueError):
        mag_x, mag_y, mag_z = 0, 0, 0
    msg.extend(struct.pack('<hhh', mag_x, mag_y, mag_z))

    # Send MSP_SIMULATOR command
    try:
        msg_bytes = bytes(msg)
        api._serial.send(int(InavMSP.MSP_SIMULATOR), msg_bytes)
        # Debug: Print message size for first few GPS packets
        if has_gps and row.get('GPS_eph'):
            import sys
            if not hasattr(send_msp_simulator, '_gps_count'):
                send_msp_simulator._gps_count = 0
            if send_msp_simulator._gps_count < 3:
                print(f"[DEBUG] Sent MSP_SIMULATOR with GPS: size={len(msg_bytes)} bytes, EPH={row.get('GPS_eph')}", file=sys.stderr)
                send_msp_simulator._gps_count += 1
        return True
    except Exception as e:
        print(f"Error sending MSP_SIMULATOR: {e}")
        return False


def enable_hitl_mode(api: MSPApi, gps_home=None):
    """
    Enable HITL mode by sending initial MSP_SIMULATOR packet.

    If gps_home dict is provided with keys: GPS_coord[0], GPS_coord[1], GPS_altitude,
    GPS_eph, GPS_epv, this will send initial GPS data so SITL can set home position.
    """
    print("Enabling HITL mode...")

    # IMPORTANT: Must match firmware's SIMULATOR_MSP_VERSION in runtime_config.h
    SIMULATOR_MSP_VERSION = 2

    # If GPS home position provided, send it so SITL can set home on arming
    if gps_home:
        print(f"  Sending initial GPS position for home: {float(gps_home['GPS_coord[0]']):.6f}, {float(gps_home['GPS_coord[1]']):.6f}")
        # Create a minimal row dict with GPS data
        row = {
            'GPS_fixType': 2,  # GPS_FIX_3D = 2 (not 3!)
            'GPS_numSat': 10,
            'GPS_coord[0]': gps_home['GPS_coord[0]'],
            'GPS_coord[1]': gps_home['GPS_coord[1]'],
            'GPS_altitude': gps_home['GPS_altitude'],
            'GPS_speed (m/s)': 0.0,
            'GPS_ground_course': 0,
            'GPS_velned[0]': 0,
            'GPS_velned[1]': 0,
            'GPS_velned[2]': 0,
            'GPS_eph': gps_home.get('GPS_eph', 100),
            'GPS_epv': gps_home.get('GPS_epv', 100),
            'accSmooth[0]': 0,
            'accSmooth[1]': 0,
            'accSmooth[2]': 512,  # 1G on Z
            'gyroADC[0]': 0,
            'gyroADC[1]': 0,
            'gyroADC[2]': 0,
            'BaroAlt (cm)': gps_home['GPS_altitude'],
            'magADC[0]': 0,
            'magADC[1]': 0,
            'magADC[2]': 0,
        }
        # Send GPS data continuously for 2-3 seconds to ensure GPS is seen as stable
        # INAV needs to see a stable GPS signal before it sets GPS_FIX and GPS origin
        print("  Sending GPS home position continuously to establish stable signal...")
        for i in range(20):  # Send 20 times over 2 seconds (10 Hz)
            success = send_msp_simulator(api, row, has_gps=True)
            if not success:
                print(f"  ✗ Failed to send GPS position (attempt {i+1})")
                return False
            time.sleep(0.1)  # 10 Hz GPS update rate

        print("  ✓ Initial GPS position sent (20x over 2s to establish stable signal)")
        time.sleep(0.3)  # Final wait for GPS origin to be set
    else:
        # Send minimal MSP_SIMULATOR packet to enable HITL (no GPS)
        msg = bytearray([SIMULATOR_MSP_VERSION])  # Version
        msg.append(0x01)  # Flags: HITL_ENABLE only
        msg += b'\x00' * 50  # Padding for all fields

        try:
            if not hasattr(api, '_serial') or api._serial is None:
                print("✗ MSPApi serial object not initialized")
                return False

            api._serial.send(int(InavMSP.MSP_SIMULATOR), msg)
            time.sleep(0.2)
        except Exception as e:
            print(f"✗ Failed to enable HITL mode: {e}")
            return False

    print("✓ HITL mode enabled")
    return True


def load_blackbox_csv(csv_file, start_time=0.0, duration=None):
    """
    Load blackbox CSV data.

    Args:
        csv_file: Path to decoded blackbox CSV file
        start_time: Start time in seconds (relative to log start)
        duration: Duration in seconds (None = entire log)

    Returns:
        List of dicts with 'time_us', 'rel_time', and 'row' keys
    """
    print(f"Loading blackbox data from: {csv_file}")

    data = []
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        first_time = None

        for row in reader:
            time_us = int(row['time (us)'])
            if first_time is None:
                first_time = time_us

            rel_time_s = (time_us - first_time) / 1e6

            # Filter by time range
            if rel_time_s < start_time:
                continue
            if duration and rel_time_s > start_time + duration:
                break

            data.append({
                'time_us': time_us,
                'rel_time': rel_time_s,
                'row': row
            })

    print(f"  Loaded {len(data)} samples")
    if duration:
        print(f"  Filtered to {start_time}s - {start_time + duration}s")

    return data


def replay_to_fc(csv_file, port, start_time=0.0, duration=None, speed=1.0):
    """
    Replay blackbox sensor data to flight controller.

    Args:
        csv_file: Path to decoded blackbox CSV file
        port: Serial port or TCP address (e.g., 'tcp:localhost:5761', '/dev/ttyACM0')
        start_time: Start time in seconds (relative to log start)
        duration: Duration in seconds (None = entire log)
        speed: Playback speed multiplier (1.0 = real-time)
    """

    print("=" * 70)
    print("Blackbox Sensor Data Replay (HITL/SITL)")
    print("=" * 70)
    print()
    print(f"CSV file: {csv_file}")
    print(f"Port: {port}")
    print(f"Speed: {speed}x")
    print(f"Start time: {start_time}s")
    if duration:
        print(f"Duration: {duration}s")
    print()

    # Load blackbox data
    data = load_blackbox_csv(csv_file, start_time, duration)
    if not data:
        print("ERROR: No data loaded")
        return

    # Load GPS data from .gps.csv file if it exists
    # GPS data arrives at ~10 Hz, should NOT be repeated for every IMU sample
    gps_csv_file = csv_file.replace('.01.csv', '.01.gps.csv')
    gps_data = {}
    if Path(gps_csv_file).exists():
        print(f"Loading GPS data from: {gps_csv_file}")
        with open(gps_csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                time_us = int(row['time (us)'])
                gps_data[time_us] = row
        print(f"  Loaded {len(gps_data)} GPS samples (~10 Hz)")
    else:
        print("  No GPS data file found (.gps.csv)")

    # Mark which samples have NEW GPS data (don't repeat GPS)
    # GPS arrives at ~10 Hz, attach GPS to nearest IMU sample
    # Track which GPS timestamps we've already used to avoid repeating GPS
    gps_times = sorted(gps_data.keys())
    used_gps_times = set()

    for sample in data:
        time_us = sample['time_us']

        # Find nearest GPS timestamp to this IMU sample
        nearest_gps_time = None
        min_diff = float('inf')

        for gps_time in gps_times:
            diff = abs(gps_time - time_us)
            if diff < min_diff and gps_time not in used_gps_times:
                min_diff = diff
                nearest_gps_time = gps_time

        # Only use GPS if within 50ms (typical GPS update period is ~100ms)
        if nearest_gps_time and min_diff < 50000:  # 50ms in microseconds
            sample['gps'] = gps_data[nearest_gps_time]
            sample['has_new_gps'] = True
            used_gps_times.add(nearest_gps_time)  # Mark as used
        else:
            sample['gps'] = None
            sample['has_new_gps'] = False

    # Estimate sample rate
    if len(data) > 1:
        time_diff = data[-1]['rel_time'] - data[0]['rel_time']
        sample_rate = len(data) / time_diff if time_diff > 0 else 0
        print(f"Sample rate: ~{sample_rate:.1f} Hz")
    print()

    # Connect to FC
    print(f"Connecting to {port}...")

    if port.startswith('tcp:'):
        # TCP connection to SITL
        host_port = port[4:]
        api = MSPApi(tcp_endpoint=host_port)
    else:
        # Serial connection to real FC (HITL)
        api = MSPApi(port=port)

    api.open()
    time.sleep(0.5)
    print("✓ Connected!")
    print()

    # Get GPS home position from blackbox header (GPS_home_lat/lon)
    # NOT from first GPS sample, which might be mid-flight!
    gps_home = None
    if len(data) > 0:
        # Find first sample with GPS data to extract GPS_home
        for sample in data:
            if sample.get('has_new_gps') and sample['gps']:
                # Use GPS_home from blackbox, not GPS_coord!
                gps_row = sample['gps']
                if 'GPS_home_lat' in gps_row and 'GPS_home_lon' in gps_row:
                    gps_home = {
                        'GPS_coord[0]': gps_row['GPS_home_lat'],  # Use home position
                        'GPS_coord[1]': gps_row['GPS_home_lon'],  # Use home position
                        'GPS_altitude': gps_row.get('GPS_altitude', 0),  # Use first sample's altitude
                        'GPS_eph': gps_row.get('GPS_eph', 100),
                        'GPS_epv': gps_row.get('GPS_epv', 100),
                    }
                    print(f"Using GPS home from blackbox: {float(gps_home['GPS_coord[0]']):.6f}, {float(gps_home['GPS_coord[1]']):.6f}")
                    break
                else:
                    # Fallback: use first GPS position if GPS_home not available
                    gps_home = sample['gps']
                    print(f"WARNING: GPS_home not in blackbox, using first GPS position: {float(gps_home['GPS_coord[0]']):.6f}, {float(gps_home['GPS_coord[1]']):.6f}")
                    break

    # Enable HITL mode and set home position
    if not enable_hitl_mode(api, gps_home):
        print("ERROR: Could not enable HITL mode")
        api.close()
        return

    print()
    print("=" * 70)
    print("Replaying sensor data...")
    print("=" * 70)
    print()
    print("Press Ctrl+C to stop")
    print()

    # Replay loop
    start_wall_time = time.time()
    last_display_time = 0
    sent_count = 0

    try:
        for i, sample in enumerate(data):
            # Merge GPS data into row if this sample has new GPS data
            row = sample['row'].copy()
            if sample.get('has_new_gps') and sample['gps']:
                # Merge GPS fields into the row
                row.update(sample['gps'])

            if send_msp_simulator(api, row, has_gps=sample.get('has_new_gps', False)):
                sent_count += 1

            # Display progress every second
            rel_time = sample['rel_time']
            if rel_time - last_display_time >= 1.0:
                if sample.get('has_new_gps') and sample['gps']:
                    gps = sample['gps']
                    eph = float(gps.get('GPS_eph', 0))
                    sats = int(gps.get('GPS_numSat', 0))
                    hdop = float(gps.get('GPS_hdop', 0))
                    print(f"[{rel_time:6.1f}s] GPS: EPH={eph:4.0f}cm, Sats={sats:2d}, HDOP={hdop:.2f}")
                else:
                    print(f"[{rel_time:6.1f}s] IMU only (no new GPS)")
                last_display_time = rel_time

            # Sleep to maintain playback speed
            if i < len(data) - 1:
                time_delta = data[i + 1]['rel_time'] - rel_time
                elapsed = time.time() - start_wall_time
                target = (rel_time - data[0]['rel_time']) / speed
                sleep_time = target - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

    except KeyboardInterrupt:
        print()
        print("Stopped by user")

    finally:
        api.close()

    print()
    print("=" * 70)
    print(f"✓ Replayed {sent_count}/{len(data)} sensor samples")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Download blackbox log from FC/SITL")
    print("2. Decode with: blackbox_decode <file>.TXT")
    print("3. Analyze navEPH for expected behavior")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Replay blackbox sensor data to FC (SITL/HITL)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Replay to SITL
  %(prog)s --csv blackbox.01.csv --port tcp:localhost:5761

  # Replay to physical FC (HITL)
  %(prog)s --csv blackbox.01.csv --port /dev/ttyACM0

  # Replay specific time range at 2x speed
  %(prog)s --csv blackbox.01.csv --port tcp:localhost:5761 \\
      --start-time 10.0 --duration 30.0 --speed 2.0
        """
    )

    parser.add_argument('--csv', required=True,
                        help='Decoded blackbox CSV file (e.g., blackbox.01.csv)')
    parser.add_argument('--port', default='tcp:localhost:5761',
                        help='Port: tcp:localhost:5761 (SITL) or /dev/ttyACM0 (HITL)')
    parser.add_argument('--start-time', type=float, default=0.0,
                        help='Start time in seconds (default: 0.0)')
    parser.add_argument('--duration', type=float, default=None,
                        help='Duration in seconds (default: entire log)')
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Playback speed multiplier (default: 1.0)')

    args = parser.parse_args()

    # Validate CSV file exists
    if not Path(args.csv).exists():
        print(f"ERROR: CSV file not found: {args.csv}")
        print()
        print("Decode blackbox first with: blackbox_decode <file>.TXT")
        sys.exit(1)

    replay_to_fc(args.csv, args.port, args.start_time, args.duration, args.speed)


if __name__ == '__main__':
    main()

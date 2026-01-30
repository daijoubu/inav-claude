#!/usr/bin/env python3
import csv
import sys

# Read the CSV file
with open('inav_0011.01.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Find indices for key fields
if not rows:
    print("No data in CSV")
    sys.exit(1)

print(f"Total rows: {len(rows)}")
first_time = int(rows[0]['time (us)']) / 1_000_000
last_time = int(rows[-1]['time (us)']) / 1_000_000
print(f"First timestamp: {first_time:.3f}s")
print(f"Last timestamp: {last_time:.3f}s")
print(f"Duration: {last_time - first_time:.3f}s")

# Look for ARM status in flightModeFlags
# The flags are text strings like "ARM|ANGLE|BLACKBOX"
print("\n=== Searching for DISARM event ===")

armed_status = []
for i, row in enumerate(rows):
    time_us = int(row['time (us)'])
    time_s = time_us / 1_000_000
    flags_str = row['flightModeFlags (flags)']
    is_armed = 'ARM' in flags_str

    # Track transitions
    if i == 0 or is_armed != armed_status[-1][1]:
        armed_status.append((time_s, is_armed, i))

print("\nArmed status transitions:")
for time_s, is_armed, row_idx in armed_status:
    status = "ARMED" if is_armed else "DISARMED"
    print(f"  Row {row_idx}: {time_s:.3f}s - {status}")

# Find disarm time
disarm_time = None
disarm_row_idx = None
for i in range(len(armed_status) - 1):
    if armed_status[i][1] and not armed_status[i+1][1]:
        disarm_time = armed_status[i+1][0]
        disarm_row_idx = armed_status[i+1][2]
        print(f"\n*** DISARM EVENT at {disarm_time:.3f}s (row {disarm_row_idx}) ***")
        break

# Calculate target time (24 seconds after disarm)
if disarm_time:
    target_time = disarm_time + 24.0
    print(f"\n*** TARGET TIME (24s after disarm): {target_time:.3f}s ***")

    # Check if target time is within log range
    if target_time > last_time:
        print(f"WARNING: Target time {target_time:.3f}s is beyond log end {last_time:.3f}s")
        print(f"Log ends {last_time - disarm_time:.3f}s after disarm")
    else:
        # Find closest row to target time
        closest_row = min(range(len(rows)), key=lambda i: abs(int(rows[i]['time (us)']) / 1_000_000 - target_time))
        closest_time = int(rows[closest_row]['time (us)']) / 1_000_000
        print(f"Closest log entry: row {closest_row} at {closest_time:.3f}s")

        # Analyze motor outputs around target time
        print("\n=== Motor outputs around target time ===")
        window_start = max(0, closest_row - 50)
        window_end = min(len(rows), closest_row + 50)

        print(f"\nShowing rows {window_start} to {window_end} (±50 from target):")
        print(f"{'Row':<6} {'Time(s)':<10} {'Motor[0]':<10} {'Motor[1]':<10} {'Motor[2]':<10} {'Motor[3]':<10}")
        print("-" * 66)

        for i in range(window_start, window_end):
            time_s = int(rows[i]['time (us)']) / 1_000_000
            m0 = rows[i]['motor[0]']
            m1 = rows[i]['motor[1]']
            m2 = rows[i]['motor[2]']
            m3 = rows[i]['motor[3]']
            marker = " <-- TARGET" if i == closest_row else ""
            print(f"{i:<6} {time_s:<10.3f} {m0:<10} {m1:<10} {m2:<10} {m3:<10}{marker}")

    # Check for anomalies - sudden changes in motor values after disarm
    print("\n=== Checking for motor anomalies after disarm ===")
    anomaly_count = 0
    for i in range(disarm_row_idx, len(rows) - 1):
        time_s = int(rows[i]['time (us)']) / 1_000_000

        # Convert motor values to int, handling empty strings
        try:
            m0_curr = int(rows[i]['motor[0]']) if rows[i]['motor[0]'] else 0
            m0_next = int(rows[i+1]['motor[0]']) if rows[i+1]['motor[0]'] else 0
            m1_curr = int(rows[i]['motor[1]']) if rows[i]['motor[1]'] else 0
            m1_next = int(rows[i+1]['motor[1]']) if rows[i+1]['motor[1]'] else 0
            m2_curr = int(rows[i]['motor[2]']) if rows[i]['motor[2]'] else 0
            m2_next = int(rows[i+1]['motor[2]']) if rows[i+1]['motor[2]'] else 0
            m3_curr = int(rows[i]['motor[3]']) if rows[i]['motor[3]'] else 0
            m3_next = int(rows[i+1]['motor[3]']) if rows[i+1]['motor[3]'] else 0

            # Look for sudden changes > 50
            diff0 = abs(m0_next - m0_curr)
            diff1 = abs(m1_next - m1_curr)
            diff2 = abs(m2_next - m2_curr)
            diff3 = abs(m3_next - m3_curr)

            if max(diff0, diff1, diff2, diff3) > 50:
                time_next = int(rows[i+1]['time (us)']) / 1_000_000
                time_since_disarm = time_s - disarm_time
                anomaly_count += 1
                print(f"\nAnomaly #{anomaly_count}")
                print(f"  Row {i}-{i+1} ({time_s:.3f}s - {time_next:.3f}s)")
                print(f"  Time since disarm: {time_since_disarm:.3f}s")
                print(f"  Motor deltas: M0={diff0}, M1={diff1}, M2={diff2}, M3={diff3}")
                if disarm_time and abs(time_since_disarm - 24.0) < 2.0:
                    print(f"  *** WITHIN 2s OF 24-SECOND MARK ***")
        except ValueError:
            pass

    if anomaly_count == 0:
        print("No motor anomalies detected after disarm")
else:
    print("\nNo disarm event found in log")

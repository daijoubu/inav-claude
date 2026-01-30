#!/usr/bin/env python3
"""
Generate detailed motor timeline showing when anomalies occur
and highlighting the 24-second target window
"""
import csv
import sys

# Read the CSV file
with open('inav_0011.01.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

disarm_time = 177.846  # From our analysis
target_time = disarm_time + 24.0

print("=" * 80)
print("DETAILED MOTOR TIMELINE ANALYSIS")
print("=" * 80)
print(f"\nDisarm time: {disarm_time:.3f}s")
print(f"Target time (24s after disarm): {target_time:.3f}s")
print()

# Create timeline buckets (every 5 seconds after disarm)
buckets = {}
for i, row in enumerate(rows):
    time_us = int(row['time (us)'])
    time_s = time_us / 1_000_000

    if time_s < disarm_time:
        continue

    time_since_disarm = time_s - disarm_time
    bucket_idx = int(time_since_disarm / 5.0)  # 5-second buckets

    if bucket_idx not in buckets:
        buckets[bucket_idx] = {
            'start_time': bucket_idx * 5.0,
            'end_time': (bucket_idx + 1) * 5.0,
            'anomaly_count': 0,
            'max_delta': 0,
            'samples': 0
        }

    buckets[bucket_idx]['samples'] += 1

    # Check for anomalies
    if i < len(rows) - 1:
        try:
            m0_curr = int(row['motor[0]']) if row['motor[0]'] else 0
            m0_next = int(rows[i+1]['motor[0]']) if rows[i+1]['motor[0]'] else 0
            m1_curr = int(row['motor[1]']) if row['motor[1]'] else 0
            m1_next = int(rows[i+1]['motor[1]']) if rows[i+1]['motor[1]'] else 0
            m2_curr = int(row['motor[2]']) if row['motor[2]'] else 0
            m2_next = int(rows[i+1]['motor[2]']) if rows[i+1]['motor[2]'] else 0
            m3_curr = int(row['motor[3]']) if row['motor[3]'] else 0
            m3_next = int(rows[i+1]['motor[3]']) if rows[i+1]['motor[3]'] else 0

            max_delta = max(
                abs(m0_next - m0_curr),
                abs(m1_next - m1_curr),
                abs(m2_next - m2_curr),
                abs(m3_next - m3_curr)
            )

            if max_delta > 50:
                buckets[bucket_idx]['anomaly_count'] += 1
                buckets[bucket_idx]['max_delta'] = max(buckets[bucket_idx]['max_delta'], max_delta)
        except ValueError:
            pass

print("\nTIMELINE (5-second buckets after disarm):")
print("-" * 80)
print(f"{'Bucket':<8} {'Time Range':<20} {'Samples':<10} {'Anomalies':<12} {'Max Delta':<12} {'Notes'}")
print("-" * 80)

for bucket_idx in sorted(buckets.keys()):
    b = buckets[bucket_idx]
    time_range = f"{b['start_time']:.0f}-{b['end_time']:.0f}s"
    notes = ""

    # Highlight the 24-second target bucket
    if b['start_time'] <= 24.0 < b['end_time']:
        notes = "*** TARGET WINDOW ***"
    elif b['anomaly_count'] > 20:
        notes = "!! HIGH ACTIVITY !!"
    elif b['anomaly_count'] == 0:
        notes = "CLEAN"

    print(f"{bucket_idx:<8} {time_range:<20} {b['samples']:<10} {b['anomaly_count']:<12} {b['max_delta']:<12} {notes}")

print("\n" + "=" * 80)
print("CRITICAL OBSERVATION:")
print("=" * 80)
print(f"\nThe 24-second target (at {target_time:.3f}s) falls in bucket 20-25s after disarm.")
print("This bucket shows:")

target_bucket = int(24.0 / 5.0)
if target_bucket in buckets:
    b = buckets[target_bucket]
    print(f"  - {b['samples']} samples logged")
    print(f"  - {b['anomaly_count']} anomalies detected")
    print(f"  - Maximum motor delta: {b['max_delta']}")

    if b['anomaly_count'] == 0:
        print("\n  ✓ NO ANOMALIES - Motors completely stable")
        print("  ✓ This contradicts the EEPROM write hypothesis")
    else:
        print(f"\n  ✗ ANOMALIES DETECTED - Investigate further")

print("\n" + "=" * 80)

# Show exact motor values at key moments
print("\nEXACT MOTOR VALUES AT KEY TIMES:")
print("=" * 80)

key_times = [
    disarm_time,
    disarm_time + 23.0,
    disarm_time + 24.0,
    disarm_time + 25.0,
]

for target_t in key_times:
    # Find closest row
    closest_row = min(range(len(rows)),
                     key=lambda i: abs(int(rows[i]['time (us)']) / 1_000_000 - target_t))
    row = rows[closest_row]
    time_s = int(row['time (us)']) / 1_000_000

    print(f"\nTime {target_t:.1f}s (actual: {time_s:.3f}s, row {closest_row}):")
    print(f"  Motor[0]: {row['motor[0]']}")
    print(f"  Motor[1]: {row['motor[1]']}")
    print(f"  Motor[2]: {row['motor[2]']}")
    print(f"  Motor[3]: {row['motor[3]']}")

    if 23.0 <= (time_s - disarm_time) <= 25.0:
        print("  >>> IN TARGET WINDOW <<<")

print("\n" + "=" * 80)

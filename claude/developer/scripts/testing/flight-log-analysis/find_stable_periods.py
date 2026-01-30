#!/usr/bin/env python3
"""
Find Stable Flight Periods

Analyzes flight log data to identify periods where airspeed, pitch, and throttle
remain relatively constant. These stable periods can then be compared to understand
the relationships between these parameters.

Usage:
    python3 find_stable_periods.py <log_file.csv> [options]

Options:
    --airspeed-var <value>    Maximum airspeed variance (cm/s, default: 50)
    --pitch-var <value>       Maximum pitch variance (degrees, default: 2.0)
    --throttle-var <value>    Maximum throttle variance (units, default: 50)
    --min-duration <value>    Minimum stable period duration (seconds, default: 2.0)
    --min-throttle <value>    Minimum throttle to exclude idle (default: 1100)
    --output <file>           Output CSV file (default: stable_periods.csv)
    --verbose                 Enable verbose output
"""

import csv
import sys
import argparse
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple


def parse_log_file(log_path: str) -> Tuple[np.ndarray, List[str]]:
    """
    Parse the flight log CSV file and extract key time-series data.

    Returns:
        data: numpy array with columns [time_s, airspeed_ms, pitch_deg, throttle]
        fieldnames: list of column names
    """
    print(f"Reading log file: {log_path}")

    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        # Strip whitespace from field names
        reader.fieldnames = [name.strip() for name in reader.fieldnames]

        data_list = []
        first_time = None

        for row in reader:
            try:
                time_us = int(row['time (us)'])
                if first_time is None:
                    first_time = time_us

                time_s = (time_us - first_time) / 1e6  # Convert to seconds from start
                airspeed_cms = int(row['AirSpeed'])  # cm/s
                airspeed_ms = airspeed_cms / 100.0  # Convert to m/s
                pitch_decideg = int(row['attitude[1]'])  # decidegrees
                pitch_deg = pitch_decideg / 10.0  # Convert to degrees
                throttle = int(row['motor[0]'])

                data_list.append([time_s, airspeed_ms, pitch_deg, throttle])
            except (ValueError, KeyError) as e:
                # Skip rows with missing or invalid data
                continue

        data = np.array(data_list)
        print(f"Loaded {len(data)} data points")
        print(f"Duration: {data[-1, 0]:.1f} seconds")
        print(f"Sampling rate: {len(data) / data[-1, 0]:.1f} Hz")

        return data, ['time_s', 'airspeed_ms', 'pitch_deg', 'throttle']


def find_stable_periods(
    data: np.ndarray,
    airspeed_var_threshold: float = 0.5,  # m/s
    pitch_var_threshold: float = 2.0,  # degrees
    throttle_var_threshold: float = 50,  # units
    min_duration: float = 2.0,  # seconds
    min_throttle: int = 1100,  # exclude idle
    sampling_rate: float = 30.7  # Hz
) -> List[Dict]:
    """
    Find stable periods in the flight data using sliding window analysis.

    Args:
        data: numpy array [time_s, airspeed_ms, pitch_deg, throttle]
        airspeed_var_threshold: max std dev for airspeed (m/s)
        pitch_var_threshold: max std dev for pitch (degrees)
        throttle_var_threshold: max std dev for throttle (units)
        min_duration: minimum period length (seconds)
        min_throttle: minimum throttle value (to exclude idle)
        sampling_rate: data sampling rate (Hz)

    Returns:
        List of stable period dictionaries
    """
    window_samples = int(min_duration * sampling_rate)
    stable_periods = []
    period_id = 0

    print(f"\nSearching for stable periods...")
    print(f"  Window size: {window_samples} samples ({min_duration}s)")
    print(f"  Thresholds: airspeed={airspeed_var_threshold} m/s, "
          f"pitch={pitch_var_threshold}°, throttle={throttle_var_threshold}")

    i = 0
    while i <= len(data) - window_samples:
        window = data[i:i+window_samples]

        # Extract parameters
        time_s = window[:, 0]
        airspeed = window[:, 1]
        pitch = window[:, 2]
        throttle = window[:, 3]

        # Calculate statistics
        airspeed_mean = np.mean(airspeed)
        airspeed_std = np.std(airspeed)
        pitch_mean = np.mean(pitch)
        pitch_std = np.std(pitch)
        throttle_mean = np.mean(throttle)
        throttle_std = np.std(throttle)

        # Check if period is stable and not idle
        is_stable = (
            airspeed_std <= airspeed_var_threshold and
            pitch_std <= pitch_var_threshold and
            throttle_std <= throttle_var_threshold and
            throttle_mean >= min_throttle
        )

        if is_stable:
            # Try to extend the stable period
            end_idx = i + window_samples
            while end_idx < len(data):
                # Check if adding next sample keeps period stable
                extended_window = data[i:end_idx+1]

                ext_airspeed_std = np.std(extended_window[:, 1])
                ext_pitch_std = np.std(extended_window[:, 2])
                ext_throttle_std = np.std(extended_window[:, 3])
                ext_throttle_mean = np.mean(extended_window[:, 3])

                if (ext_airspeed_std <= airspeed_var_threshold and
                    ext_pitch_std <= pitch_var_threshold and
                    ext_throttle_std <= throttle_var_threshold and
                    ext_throttle_mean >= min_throttle):
                    end_idx += 1
                else:
                    break

            # Use the extended period
            final_window = data[i:end_idx]
            duration = final_window[-1, 0] - final_window[0, 0]

            period = {
                'period_id': period_id,
                'start_time': final_window[0, 0],
                'end_time': final_window[-1, 0],
                'duration': duration,
                'airspeed_mean': np.mean(final_window[:, 1]),
                'airspeed_std': np.std(final_window[:, 1]),
                'pitch_mean': np.mean(final_window[:, 2]),
                'pitch_std': np.std(final_window[:, 2]),
                'throttle_mean': np.mean(final_window[:, 3]),
                'throttle_std': np.std(final_window[:, 3]),
                'num_samples': len(final_window)
            }

            stable_periods.append(period)
            period_id += 1

            # Jump to end of this period to avoid overlaps
            i = end_idx
        else:
            # Move window forward
            i += 1

    print(f"Found {len(stable_periods)} stable periods")

    return stable_periods


def write_stable_periods(periods: List[Dict], output_path: str):
    """Write stable periods to CSV file."""
    if not periods:
        print(f"No stable periods to write!")
        return

    print(f"\nWriting results to: {output_path}")

    fieldnames = [
        'period_id', 'start_time', 'end_time', 'duration', 'num_samples',
        'airspeed_mean', 'airspeed_std',
        'pitch_mean', 'pitch_std',
        'throttle_mean', 'throttle_std'
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(periods)

    # Print summary statistics
    print(f"\nStable Period Summary:")
    print(f"  Total periods: {len(periods)}")
    total_duration = sum(p['duration'] for p in periods)
    print(f"  Total stable time: {total_duration:.1f}s")

    # Print ranges
    airspeeds = [p['airspeed_mean'] for p in periods]
    pitches = [p['pitch_mean'] for p in periods]
    throttles = [p['throttle_mean'] for p in periods]

    print(f"\n  Airspeed range: {min(airspeeds):.1f} - {max(airspeeds):.1f} m/s")
    print(f"  Pitch range: {min(pitches):.1f} - {max(pitches):.1f}°")
    print(f"  Throttle range: {int(min(throttles))} - {int(max(throttles))}")


def main():
    parser = argparse.ArgumentParser(
        description='Find stable flight periods in blackbox logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('log_file', help='Path to CSV log file')
    parser.add_argument('--airspeed-var', type=float, default=0.5,
                        help='Maximum airspeed std dev (m/s, default: 0.5)')
    parser.add_argument('--pitch-var', type=float, default=2.0,
                        help='Maximum pitch std dev (degrees, default: 2.0)')
    parser.add_argument('--throttle-var', type=float, default=50,
                        help='Maximum throttle std dev (units, default: 50)')
    parser.add_argument('--min-duration', type=float, default=2.0,
                        help='Minimum period duration (seconds, default: 2.0)')
    parser.add_argument('--min-throttle', type=int, default=1100,
                        help='Minimum throttle to exclude idle (default: 1100)')
    parser.add_argument('--output', type=str, default='stable_periods.csv',
                        help='Output CSV file (default: stable_periods.csv)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    # Load data
    data, fieldnames = parse_log_file(args.log_file)

    # Calculate sampling rate
    sampling_rate = len(data) / data[-1, 0]

    # Find stable periods
    periods = find_stable_periods(
        data,
        airspeed_var_threshold=args.airspeed_var,
        pitch_var_threshold=args.pitch_var,
        throttle_var_threshold=args.throttle_var,
        min_duration=args.min_duration,
        min_throttle=args.min_throttle,
        sampling_rate=sampling_rate
    )

    # Write output
    write_stable_periods(periods, args.output)

    if args.verbose and periods:
        print("\nFirst 5 stable periods:")
        for period in periods[:5]:
            print(f"  Period {period['period_id']}: "
                  f"{period['start_time']:.1f}-{period['end_time']:.1f}s "
                  f"({period['duration']:.1f}s) - "
                  f"airspeed={period['airspeed_mean']:.1f}m/s, "
                  f"pitch={period['pitch_mean']:.1f}°, "
                  f"throttle={int(period['throttle_mean'])}")


if __name__ == '__main__':
    main()

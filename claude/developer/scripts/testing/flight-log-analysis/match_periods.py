#!/usr/bin/env python3
"""
Match Stable Flight Periods

Finds pairs of stable periods that can be compared to understand relationships
between pitch, throttle, and airspeed.

Three matching scenarios:
  A: Same throttle, different pitch → How does pitch affect airspeed?
  B: Same airspeed, different pitch/throttle → How do they trade off?
  C: Same pitch, different throttle → How does throttle affect airspeed?

Usage:
    python3 match_periods.py <stable_periods.csv> [options]

Options:
    --throttle-tol <value>    Throttle matching tolerance (units, default: 50)
    --airspeed-tol <value>    Airspeed matching tolerance (m/s, default: 1.0)
    --pitch-tol <value>       Pitch matching tolerance (degrees, default: 2.0)
    --min-diff-pitch <value>  Minimum pitch difference for comparison (degrees, default: 3.0)
    --min-diff-throttle <value> Minimum throttle difference for comparison (units, default: 100)
    --min-diff-airspeed <value> Minimum airspeed difference for comparison (m/s, default: 2.0)
    --output <file>           Output CSV file (default: matched_periods.csv)
    --verbose                 Enable verbose output
"""

import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import itertools


def load_stable_periods(csv_path: str) -> List[Dict]:
    """Load stable periods from CSV file."""
    print(f"Loading stable periods from: {csv_path}")

    periods = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            period = {
                'period_id': int(row['period_id']),
                'start_time': float(row['start_time']),
                'end_time': float(row['end_time']),
                'duration': float(row['duration']),
                'num_samples': int(row['num_samples']),
                'airspeed_mean': float(row['airspeed_mean']),
                'airspeed_std': float(row['airspeed_std']),
                'pitch_mean': float(row['pitch_mean']),
                'pitch_std': float(row['pitch_std']),
                'throttle_mean': float(row['throttle_mean']),
                'throttle_std': float(row['throttle_std']),
            }
            periods.append(period)

    print(f"Loaded {len(periods)} stable periods")
    return periods


def find_scenario_a_matches(
    periods: List[Dict],
    throttle_tolerance: float,
    min_pitch_diff: float
) -> List[Dict]:
    """
    Scenario A: Same throttle, different pitch
    Answers: How does pitch affect airspeed at constant throttle?
    """
    matches = []

    for p1, p2 in itertools.combinations(periods, 2):
        throttle_diff = abs(p1['throttle_mean'] - p2['throttle_mean'])
        pitch_diff = abs(p1['pitch_mean'] - p2['pitch_mean'])
        airspeed_diff = p2['airspeed_mean'] - p1['airspeed_mean']

        # Same throttle, different pitch
        if throttle_diff <= throttle_tolerance and pitch_diff >= min_pitch_diff:
            match = {
                'scenario': 'A',
                'period_1': p1['period_id'],
                'period_2': p2['period_id'],
                'throttle_1': p1['throttle_mean'],
                'throttle_2': p2['throttle_mean'],
                'throttle_diff': throttle_diff,
                'pitch_1': p1['pitch_mean'],
                'pitch_2': p2['pitch_mean'],
                'pitch_diff': p2['pitch_mean'] - p1['pitch_mean'],
                'airspeed_1': p1['airspeed_mean'],
                'airspeed_2': p2['airspeed_mean'],
                'airspeed_diff': airspeed_diff,
                'time_1': f"{p1['start_time']:.1f}-{p1['end_time']:.1f}",
                'time_2': f"{p2['start_time']:.1f}-{p2['end_time']:.1f}",
            }
            matches.append(match)

    return matches


def find_scenario_b_matches(
    periods: List[Dict],
    airspeed_tolerance: float,
    min_pitch_diff: float,
    min_throttle_diff: float
) -> List[Dict]:
    """
    Scenario B: Same airspeed, different pitch/throttle
    Answers: How do pitch and throttle trade off to maintain airspeed?
    """
    matches = []

    for p1, p2 in itertools.combinations(periods, 2):
        airspeed_diff = abs(p1['airspeed_mean'] - p2['airspeed_mean'])
        pitch_diff = abs(p1['pitch_mean'] - p2['pitch_mean'])
        throttle_diff = abs(p1['throttle_mean'] - p2['throttle_mean'])

        # Same airspeed, different pitch and throttle
        if (airspeed_diff <= airspeed_tolerance and
            pitch_diff >= min_pitch_diff and
            throttle_diff >= min_throttle_diff):
            match = {
                'scenario': 'B',
                'period_1': p1['period_id'],
                'period_2': p2['period_id'],
                'airspeed_1': p1['airspeed_mean'],
                'airspeed_2': p2['airspeed_mean'],
                'airspeed_diff': p2['airspeed_mean'] - p1['airspeed_mean'],
                'pitch_1': p1['pitch_mean'],
                'pitch_2': p2['pitch_mean'],
                'pitch_diff': p2['pitch_mean'] - p1['pitch_mean'],
                'throttle_1': p1['throttle_mean'],
                'throttle_2': p2['throttle_mean'],
                'throttle_diff': p2['throttle_mean'] - p1['throttle_mean'],
                'time_1': f"{p1['start_time']:.1f}-{p1['end_time']:.1f}",
                'time_2': f"{p2['start_time']:.1f}-{p2['end_time']:.1f}",
            }
            matches.append(match)

    return matches


def find_scenario_c_matches(
    periods: List[Dict],
    pitch_tolerance: float,
    min_throttle_diff: float
) -> List[Dict]:
    """
    Scenario C: Same pitch, different throttle
    Answers: How does throttle affect airspeed at constant pitch?
    """
    matches = []

    for p1, p2 in itertools.combinations(periods, 2):
        pitch_diff = abs(p1['pitch_mean'] - p2['pitch_mean'])
        throttle_diff = abs(p1['throttle_mean'] - p2['throttle_mean'])
        airspeed_diff = p2['airspeed_mean'] - p1['airspeed_mean']

        # Same pitch, different throttle
        if pitch_diff <= pitch_tolerance and throttle_diff >= min_throttle_diff:
            match = {
                'scenario': 'C',
                'period_1': p1['period_id'],
                'period_2': p2['period_id'],
                'pitch_1': p1['pitch_mean'],
                'pitch_2': p2['pitch_mean'],
                'pitch_diff': pitch_diff,
                'throttle_1': p1['throttle_mean'],
                'throttle_2': p2['throttle_mean'],
                'throttle_diff': p2['throttle_mean'] - p1['throttle_mean'],
                'airspeed_1': p1['airspeed_mean'],
                'airspeed_2': p2['airspeed_mean'],
                'airspeed_diff': airspeed_diff,
                'time_1': f"{p1['start_time']:.1f}-{p1['end_time']:.1f}",
                'time_2': f"{p2['start_time']:.1f}-{p2['end_time']:.1f}",
            }
            matches.append(match)

    return matches


def write_matched_periods(matches: List[Dict], output_path: str):
    """Write matched periods to CSV file."""
    if not matches:
        print(f"No matched periods to write!")
        return

    print(f"\nWriting results to: {output_path}")

    # Determine all unique fieldnames
    fieldnames = set()
    for match in matches:
        fieldnames.update(match.keys())
    fieldnames = sorted(list(fieldnames))

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)


def print_match_summary(matches: List[Dict], scenario: str, description: str):
    """Print summary of matches for a scenario."""
    scenario_matches = [m for m in matches if m['scenario'] == scenario]

    print(f"\n{description}")
    print(f"  Total matches: {len(scenario_matches)}")

    if scenario_matches:
        print(f"\n  Top 5 matches:")
        for i, match in enumerate(scenario_matches[:5]):
            if scenario == 'A':
                print(f"    {i+1}. Periods {match['period_1']} & {match['period_2']}: "
                      f"throttle={match['throttle_1']:.0f}, "
                      f"pitch {match['pitch_1']:.1f}°→{match['pitch_2']:.1f}°, "
                      f"airspeed {match['airspeed_1']:.1f}→{match['airspeed_2']:.1f} m/s "
                      f"(Δ={match['airspeed_diff']:.1f})")
            elif scenario == 'B':
                print(f"    {i+1}. Periods {match['period_1']} & {match['period_2']}: "
                      f"airspeed={match['airspeed_1']:.1f} m/s, "
                      f"pitch {match['pitch_1']:.1f}°→{match['pitch_2']:.1f}°, "
                      f"throttle {match['throttle_1']:.0f}→{match['throttle_2']:.0f} "
                      f"(Δ={match['throttle_diff']:.0f})")
            elif scenario == 'C':
                print(f"    {i+1}. Periods {match['period_1']} & {match['period_2']}: "
                      f"pitch={match['pitch_1']:.1f}°, "
                      f"throttle {match['throttle_1']:.0f}→{match['throttle_2']:.0f}, "
                      f"airspeed {match['airspeed_1']:.1f}→{match['airspeed_2']:.1f} m/s "
                      f"(Δ={match['airspeed_diff']:.1f})")


def main():
    parser = argparse.ArgumentParser(
        description='Match stable flight periods for comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('stable_periods', help='Path to stable periods CSV file')
    parser.add_argument('--throttle-tol', type=float, default=50,
                        help='Throttle matching tolerance (units, default: 50)')
    parser.add_argument('--airspeed-tol', type=float, default=1.0,
                        help='Airspeed matching tolerance (m/s, default: 1.0)')
    parser.add_argument('--pitch-tol', type=float, default=2.0,
                        help='Pitch matching tolerance (degrees, default: 2.0)')
    parser.add_argument('--min-diff-pitch', type=float, default=3.0,
                        help='Minimum pitch difference for comparison (degrees, default: 3.0)')
    parser.add_argument('--min-diff-throttle', type=float, default=100,
                        help='Minimum throttle difference for comparison (units, default: 100)')
    parser.add_argument('--min-diff-airspeed', type=float, default=2.0,
                        help='Minimum airspeed difference for comparison (m/s, default: 2.0)')
    parser.add_argument('--output', type=str, default='matched_periods.csv',
                        help='Output CSV file (default: matched_periods.csv)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    # Load stable periods
    periods = load_stable_periods(args.stable_periods)

    print(f"\nSearching for period matches...")
    print(f"  Tolerances: throttle=±{args.throttle_tol}, "
          f"airspeed=±{args.airspeed_tol} m/s, pitch=±{args.pitch_tol}°")
    print(f"  Minimum differences: pitch={args.min_diff_pitch}°, "
          f"throttle={args.min_diff_throttle}, airspeed={args.min_diff_airspeed} m/s")

    # Find matches for each scenario
    all_matches = []

    scenario_a = find_scenario_a_matches(
        periods,
        args.throttle_tol,
        args.min_diff_pitch
    )
    all_matches.extend(scenario_a)
    print_match_summary(scenario_a, 'A',
                        'Scenario A: Same throttle, different pitch')

    scenario_b = find_scenario_b_matches(
        periods,
        args.airspeed_tol,
        args.min_diff_pitch,
        args.min_diff_throttle
    )
    all_matches.extend(scenario_b)
    print_match_summary(scenario_b, 'B',
                        'Scenario B: Same airspeed, different pitch/throttle')

    scenario_c = find_scenario_c_matches(
        periods,
        args.pitch_tol,
        args.min_diff_throttle
    )
    all_matches.extend(scenario_c)
    print_match_summary(scenario_c, 'C',
                        'Scenario C: Same pitch, different throttle')

    # Write output
    write_matched_periods(all_matches, args.output)

    print(f"\nTotal matches across all scenarios: {len(all_matches)}")


if __name__ == '__main__':
    main()

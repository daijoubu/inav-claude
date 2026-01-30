#!/usr/bin/env python3
"""
Analyze Pitch/Throttle/Airspeed Relationships

Performs statistical analysis on matched period pairs to calculate sensitivity
coefficients and understand how pitch and throttle affect airspeed.

Usage:
    python3 analyze_relationships.py <matched_periods.csv> [options]

Options:
    --output-dir <path>       Output directory for results (default: current dir)
    --plot                    Generate visualization plots
    --verbose                 Enable verbose output
"""

import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import numpy as np
from scipy import stats


def load_matched_periods(csv_path: str) -> Dict[str, List[Dict]]:
    """Load matched periods from CSV file, grouped by scenario."""
    print(f"Loading matched periods from: {csv_path}")

    matches_by_scenario = {'A': [], 'B': [], 'C': []}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = row['scenario']

            # Convert numeric fields
            match = {k: v for k, v in row.items()}
            for key in match:
                if key != 'scenario' and key != 'time_1' and key != 'time_2':
                    try:
                        match[key] = float(match[key])
                    except (ValueError, KeyError):
                        pass

            matches_by_scenario[scenario].append(match)

    for scenario, matches in matches_by_scenario.items():
        print(f"  Scenario {scenario}: {len(matches)} matches")

    return matches_by_scenario


def analyze_scenario_a(matches: List[Dict]) -> Dict:
    """
    Analyze Scenario A: Same throttle, different pitch
    Calculate: Δairspeed / Δpitch (m/s per degree)
    """
    print(f"\n{'='*70}")
    print("SCENARIO A: Same Throttle, Different Pitch")
    print("Question: How does pitch affect airspeed at constant throttle?")
    print(f"{'='*70}")

    # Calculate sensitivity: Δairspeed / Δpitch
    sensitivities = []
    for match in matches:
        delta_pitch = match['pitch_diff']
        delta_airspeed = match['airspeed_diff']

        if abs(delta_pitch) > 0.1:  # Avoid division by near-zero
            sensitivity = delta_airspeed / delta_pitch  # m/s per degree
            sensitivities.append({
                'sensitivity': sensitivity,
                'delta_pitch': delta_pitch,
                'delta_airspeed': delta_airspeed,
                'throttle': match['throttle_1'],
                'pitch_1': match['pitch_1'],
                'pitch_2': match['pitch_2'],
                'airspeed_1': match['airspeed_1'],
                'airspeed_2': match['airspeed_2'],
            })

    if not sensitivities:
        print("  No valid data points for analysis")
        return {}

    # Statistical analysis
    sens_values = [s['sensitivity'] for s in sensitivities]
    mean_sens = np.mean(sens_values)
    median_sens = np.median(sens_values)
    std_sens = np.std(sens_values)

    print(f"\nSensitivity: Δairspeed / Δpitch")
    print(f"  Mean:   {mean_sens:+.3f} m/s per degree")
    print(f"  Median: {median_sens:+.3f} m/s per degree")
    print(f"  Std Dev: {std_sens:.3f} m/s per degree")
    print(f"  Range:  {min(sens_values):+.3f} to {max(sens_values):+.3f} m/s per degree")

    # Interpretation
    print(f"\nInterpretation:")
    print(f"  On average, increasing pitch by 1° changes airspeed by {mean_sens:+.2f} m/s")
    if mean_sens > 0:
        print(f"  Positive correlation: More nose-up pitch → higher airspeed")
    else:
        print(f"  Negative correlation: More nose-down pitch → higher airspeed")

    # Find extreme examples
    sensitivities.sort(key=lambda x: abs(x['sensitivity']), reverse=True)
    print(f"\nTop 3 examples with largest effects:")
    for i, s in enumerate(sensitivities[:3]):
        print(f"  {i+1}. Pitch {s['pitch_1']:.1f}°→{s['pitch_2']:.1f}° (Δ={s['delta_pitch']:+.1f}°): "
              f"Airspeed {s['airspeed_1']:.1f}→{s['airspeed_2']:.1f} m/s "
              f"(Δ={s['delta_airspeed']:+.1f}, sensitivity={s['sensitivity']:+.2f} m/s/°)")

    return {
        'scenario': 'A',
        'n_samples': len(sensitivities),
        'mean_sensitivity': mean_sens,
        'median_sensitivity': median_sens,
        'std_sensitivity': std_sens,
        'min_sensitivity': min(sens_values),
        'max_sensitivity': max(sens_values),
        'sensitivities': sensitivities
    }


def analyze_scenario_b(matches: List[Dict]) -> Dict:
    """
    Analyze Scenario B: Same airspeed, different pitch/throttle
    Calculate: Δthrottle / Δpitch (throttle units per degree)
    """
    print(f"\n{'='*70}")
    print("SCENARIO B: Same Airspeed, Different Pitch/Throttle")
    print("Question: How do pitch and throttle trade off to maintain airspeed?")
    print(f"{'='*70}")

    # Calculate tradeoff: Δthrottle / Δpitch
    tradeoffs = []
    for match in matches:
        delta_pitch = match['pitch_diff']
        delta_throttle = match['throttle_diff']

        if abs(delta_pitch) > 0.1:  # Avoid division by near-zero
            tradeoff = delta_throttle / delta_pitch  # throttle units per degree
            tradeoffs.append({
                'tradeoff': tradeoff,
                'delta_pitch': delta_pitch,
                'delta_throttle': delta_throttle,
                'airspeed': match['airspeed_1'],
                'pitch_1': match['pitch_1'],
                'pitch_2': match['pitch_2'],
                'throttle_1': match['throttle_1'],
                'throttle_2': match['throttle_2'],
            })

    if not tradeoffs:
        print("  No valid data points for analysis")
        return {}

    # Statistical analysis
    trade_values = [t['tradeoff'] for t in tradeoffs]
    mean_trade = np.mean(trade_values)
    median_trade = np.median(trade_values)
    std_trade = np.std(trade_values)

    print(f"\nTradeoff: Δthrottle / Δpitch")
    print(f"  Mean:   {mean_trade:+.1f} throttle units per degree")
    print(f"  Median: {median_trade:+.1f} throttle units per degree")
    print(f"  Std Dev: {std_trade:.1f} throttle units per degree")
    print(f"  Range:  {min(trade_values):+.1f} to {max(trade_values):+.1f} throttle units per degree")

    # Interpretation
    print(f"\nInterpretation:")
    print(f"  To maintain constant airspeed:")
    print(f"  - Increasing pitch by 1° requires {-mean_trade:.1f} units less throttle")
    print(f"  - Decreasing pitch by 1° requires {mean_trade:.1f} units more throttle")

    # Find extreme examples
    tradeoffs.sort(key=lambda x: abs(x['tradeoff']), reverse=True)
    print(f"\nTop 3 examples with largest tradeoffs:")
    for i, t in enumerate(tradeoffs[:3]):
        print(f"  {i+1}. Airspeed={t['airspeed']:.1f} m/s: "
              f"Pitch {t['pitch_1']:.1f}°→{t['pitch_2']:.1f}° (Δ={t['delta_pitch']:+.1f}°), "
              f"Throttle {t['throttle_1']:.0f}→{t['throttle_2']:.0f} "
              f"(Δ={t['delta_throttle']:+.0f}, tradeoff={t['tradeoff']:+.1f} units/°)")

    return {
        'scenario': 'B',
        'n_samples': len(tradeoffs),
        'mean_tradeoff': mean_trade,
        'median_tradeoff': median_trade,
        'std_tradeoff': std_trade,
        'min_tradeoff': min(trade_values),
        'max_tradeoff': max(trade_values),
        'tradeoffs': tradeoffs
    }


def analyze_scenario_c(matches: List[Dict]) -> Dict:
    """
    Analyze Scenario C: Same pitch, different throttle
    Calculate: Δairspeed / Δthrottle (m/s per throttle unit)
    """
    print(f"\n{'='*70}")
    print("SCENARIO C: Same Pitch, Different Throttle")
    print("Question: How does throttle affect airspeed at constant pitch?")
    print(f"{'='*70}")

    # Calculate sensitivity: Δairspeed / Δthrottle
    sensitivities = []
    for match in matches:
        delta_throttle = match['throttle_diff']
        delta_airspeed = match['airspeed_diff']

        if abs(delta_throttle) > 1.0:  # Avoid division by near-zero
            sensitivity = delta_airspeed / delta_throttle  # m/s per throttle unit
            sensitivities.append({
                'sensitivity': sensitivity,
                'delta_throttle': delta_throttle,
                'delta_airspeed': delta_airspeed,
                'pitch': match['pitch_1'],
                'throttle_1': match['throttle_1'],
                'throttle_2': match['throttle_2'],
                'airspeed_1': match['airspeed_1'],
                'airspeed_2': match['airspeed_2'],
            })

    if not sensitivities:
        print("  No valid data points for analysis")
        return {}

    # Statistical analysis
    sens_values = [s['sensitivity'] for s in sensitivities]
    mean_sens = np.mean(sens_values)
    median_sens = np.median(sens_values)
    std_sens = np.std(sens_values)

    print(f"\nSensitivity: Δairspeed / Δthrottle")
    print(f"  Mean:   {mean_sens:+.6f} m/s per throttle unit")
    print(f"  Median: {median_sens:+.6f} m/s per throttle unit")
    print(f"  Std Dev: {std_sens:.6f} m/s per throttle unit")
    print(f"  Range:  {min(sens_values):+.6f} to {max(sens_values):+.6f} m/s per throttle unit")

    # Express in more useful units
    mean_sens_per_100 = mean_sens * 100
    print(f"\nAlternative expression:")
    print(f"  Mean: {mean_sens_per_100:+.3f} m/s per 100 throttle units")
    print(f"  Interpretation: Increasing throttle by 100 units changes airspeed by {mean_sens_per_100:+.2f} m/s")

    # Find extreme examples
    sensitivities.sort(key=lambda x: abs(x['sensitivity']), reverse=True)
    print(f"\nTop 3 examples with largest effects:")
    for i, s in enumerate(sensitivities[:3]):
        print(f"  {i+1}. Pitch={s['pitch']:.1f}°: "
              f"Throttle {s['throttle_1']:.0f}→{s['throttle_2']:.0f} (Δ={s['delta_throttle']:+.0f}), "
              f"Airspeed {s['airspeed_1']:.1f}→{s['airspeed_2']:.1f} m/s "
              f"(Δ={s['delta_airspeed']:+.1f}, sensitivity={s['sensitivity']:+.4f} m/s/unit)")

    return {
        'scenario': 'C',
        'n_samples': len(sensitivities),
        'mean_sensitivity': mean_sens,
        'median_sensitivity': median_sens,
        'std_sensitivity': std_sens,
        'min_sensitivity': min(sens_values),
        'max_sensitivity': max(sens_values),
        'sensitivities': sensitivities
    }


def generate_plots(results: Dict, output_dir: str):
    """Generate visualization plots."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        print("\nWarning: matplotlib not available, skipping plots")
        return

    print(f"\nGenerating plots in: {output_dir}")

    # Scenario A: Pitch vs Airspeed change
    if 'A' in results and results['A'].get('sensitivities'):
        fig, ax = plt.subplots(figsize=(10, 6))
        data = results['A']['sensitivities']
        x = [d['delta_pitch'] for d in data]
        y = [d['delta_airspeed'] for d in data]

        ax.scatter(x, y, alpha=0.5)

        # Add regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_line = np.array([min(x), max(x)])
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', label=f'Linear fit: y={slope:.2f}x+{intercept:.2f} (R²={r_value**2:.3f})')

        ax.set_xlabel('Pitch Change (degrees)')
        ax.set_ylabel('Airspeed Change (m/s)')
        ax.set_title('Scenario A: Effect of Pitch on Airspeed (Constant Throttle)')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f"{output_dir}/scenario_a_pitch_vs_airspeed.png", dpi=150)
        plt.close()
        print(f"  Created: scenario_a_pitch_vs_airspeed.png")

    # Scenario B: Pitch vs Throttle tradeoff
    if 'B' in results and results['B'].get('tradeoffs'):
        fig, ax = plt.subplots(figsize=(10, 6))
        data = results['B']['tradeoffs']
        x = [d['delta_pitch'] for d in data]
        y = [d['delta_throttle'] for d in data]

        ax.scatter(x, y, alpha=0.5)

        # Add regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_line = np.array([min(x), max(x)])
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', label=f'Linear fit: y={slope:.1f}x+{intercept:.1f} (R²={r_value**2:.3f})')

        ax.set_xlabel('Pitch Change (degrees)')
        ax.set_ylabel('Throttle Change (units)')
        ax.set_title('Scenario B: Pitch/Throttle Tradeoff (Constant Airspeed)')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f"{output_dir}/scenario_b_pitch_throttle_tradeoff.png", dpi=150)
        plt.close()
        print(f"  Created: scenario_b_pitch_throttle_tradeoff.png")

    # Scenario C: Throttle vs Airspeed change
    if 'C' in results and results['C'].get('sensitivities'):
        fig, ax = plt.subplots(figsize=(10, 6))
        data = results['C']['sensitivities']
        x = [d['delta_throttle'] for d in data]
        y = [d['delta_airspeed'] for d in data]

        ax.scatter(x, y, alpha=0.5)

        # Add regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        x_line = np.array([min(x), max(x)])
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', label=f'Linear fit: y={slope:.4f}x+{intercept:.2f} (R²={r_value**2:.3f})')

        ax.set_xlabel('Throttle Change (units)')
        ax.set_ylabel('Airspeed Change (m/s)')
        ax.set_title('Scenario C: Effect of Throttle on Airspeed (Constant Pitch)')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig(f"{output_dir}/scenario_c_throttle_vs_airspeed.png", dpi=150)
        plt.close()
        print(f"  Created: scenario_c_throttle_vs_airspeed.png")


def write_summary(results: Dict, output_path: str):
    """Write analysis summary to text file."""
    print(f"\nWriting summary to: {output_path}")

    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PITCH/THROTTLE/AIRSPEED RELATIONSHIP ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        if 'A' in results and results['A']:
            f.write("SCENARIO A: Same Throttle, Different Pitch\n")
            f.write("-" * 80 + "\n")
            f.write(f"Samples: {results['A']['n_samples']}\n")
            f.write(f"Mean Sensitivity: {results['A']['mean_sensitivity']:+.3f} m/s per degree\n")
            f.write(f"Median Sensitivity: {results['A']['median_sensitivity']:+.3f} m/s per degree\n")
            f.write(f"Std Dev: {results['A']['std_sensitivity']:.3f} m/s per degree\n")
            f.write(f"Range: {results['A']['min_sensitivity']:+.3f} to {results['A']['max_sensitivity']:+.3f} m/s per degree\n")
            f.write("\n")

        if 'B' in results and results['B']:
            f.write("SCENARIO B: Same Airspeed, Different Pitch/Throttle\n")
            f.write("-" * 80 + "\n")
            f.write(f"Samples: {results['B']['n_samples']}\n")
            f.write(f"Mean Tradeoff: {results['B']['mean_tradeoff']:+.1f} throttle units per degree\n")
            f.write(f"Median Tradeoff: {results['B']['median_tradeoff']:+.1f} throttle units per degree\n")
            f.write(f"Std Dev: {results['B']['std_tradeoff']:.1f} throttle units per degree\n")
            f.write(f"Range: {results['B']['min_tradeoff']:+.1f} to {results['B']['max_tradeoff']:+.1f} throttle units per degree\n")
            f.write("\n")

        if 'C' in results and results['C']:
            f.write("SCENARIO C: Same Pitch, Different Throttle\n")
            f.write("-" * 80 + "\n")
            f.write(f"Samples: {results['C']['n_samples']}\n")
            f.write(f"Mean Sensitivity: {results['C']['mean_sensitivity']:+.6f} m/s per throttle unit\n")
            f.write(f"                  {results['C']['mean_sensitivity']*100:+.3f} m/s per 100 throttle units\n")
            f.write(f"Median Sensitivity: {results['C']['median_sensitivity']:+.6f} m/s per throttle unit\n")
            f.write(f"Std Dev: {results['C']['std_sensitivity']:.6f} m/s per throttle unit\n")
            f.write(f"Range: {results['C']['min_sensitivity']:+.6f} to {results['C']['max_sensitivity']:+.6f} m/s per throttle unit\n")
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze pitch/throttle/airspeed relationships',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('matched_periods', help='Path to matched periods CSV file')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory for results (default: current directory)')
    parser.add_argument('--plot', action='store_true',
                        help='Generate visualization plots')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()

    # Create output directory if needed
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load matches
    matches_by_scenario = load_matched_periods(args.matched_periods)

    # Analyze each scenario
    results = {}

    if matches_by_scenario['A']:
        results['A'] = analyze_scenario_a(matches_by_scenario['A'])

    if matches_by_scenario['B']:
        results['B'] = analyze_scenario_b(matches_by_scenario['B'])

    if matches_by_scenario['C']:
        results['C'] = analyze_scenario_c(matches_by_scenario['C'])

    # Write summary
    summary_path = f"{args.output_dir}/analysis_results.txt"
    write_summary(results, summary_path)

    # Generate plots if requested
    if args.plot:
        generate_plots(results, args.output_dir)

    print(f"\n{'='*70}")
    print("Analysis complete!")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

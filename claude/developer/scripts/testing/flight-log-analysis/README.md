# Pitch/Throttle/Airspeed Analysis Scripts

This directory contains reusable scripts for analyzing flight log data to understand the relationships between pitch, throttle, and airspeed.

## Overview

The analysis pipeline consists of three scripts:

1. **find_stable_periods.py** - Detects stable flight periods
2. **match_periods.py** - Finds comparable period pairs
3. **analyze_relationships.py** - Calculates sensitivity coefficients and generates visualizations

## Requirements

```bash
pip install numpy scipy matplotlib
```

## Usage

### Step 1: Find Stable Periods

Identifies flight segments where airspeed, pitch, and throttle remain relatively constant.

```bash
python3 find_stable_periods.py <log_file.csv> [options]
```

**Options:**
- `--airspeed-var <value>` - Maximum airspeed std dev (m/s, default: 0.5)
- `--pitch-var <value>` - Maximum pitch std dev (degrees, default: 2.0)
- `--throttle-var <value>` - Maximum throttle std dev (units, default: 50)
- `--min-duration <value>` - Minimum period duration (seconds, default: 2.0)
- `--min-throttle <value>` - Minimum throttle to exclude idle (default: 1100)
- `--output <file>` - Output CSV file (default: stable_periods.csv)
- `--verbose` - Enable verbose output

**Example:**
```bash
python3 find_stable_periods.py /path/to/LOG0005.01.csv \
    --output stable_periods.csv \
    --verbose
```

**Output:** `stable_periods.csv` with columns:
- period_id, start_time, end_time, duration, num_samples
- airspeed_mean, airspeed_std
- pitch_mean, pitch_std
- throttle_mean, throttle_std

### Step 2: Match Periods

Finds pairs of stable periods that can be compared to understand relationships.

```bash
python3 match_periods.py <stable_periods.csv> [options]
```

**Options:**
- `--throttle-tol <value>` - Throttle matching tolerance (units, default: 50)
- `--airspeed-tol <value>` - Airspeed matching tolerance (m/s, default: 1.0)
- `--pitch-tol <value>` - Pitch matching tolerance (degrees, default: 2.0)
- `--min-diff-pitch <value>` - Minimum pitch difference (degrees, default: 3.0)
- `--min-diff-throttle <value>` - Minimum throttle difference (units, default: 100)
- `--min-diff-airspeed <value>` - Minimum airspeed difference (m/s, default: 2.0)
- `--output <file>` - Output CSV file (default: matched_periods.csv)
- `--verbose` - Enable verbose output

**Example:**
```bash
python3 match_periods.py stable_periods.csv \
    --output matched_periods.csv \
    --verbose
```

**Matching Scenarios:**
- **Scenario A:** Same throttle, different pitch → How does pitch affect airspeed?
- **Scenario B:** Same airspeed, different pitch/throttle → How do they trade off?
- **Scenario C:** Same pitch, different throttle → How does throttle affect airspeed?

**Output:** `matched_periods.csv` with matched pairs and their parameters

### Step 3: Analyze Relationships

Performs statistical analysis and generates visualizations.

```bash
python3 analyze_relationships.py <matched_periods.csv> [options]
```

**Options:**
- `--output-dir <path>` - Output directory for results (default: current dir)
- `--plot` - Generate visualization plots
- `--verbose` - Enable verbose output

**Example:**
```bash
python3 analyze_relationships.py matched_periods.csv \
    --output-dir outputs \
    --plot \
    --verbose
```

**Outputs:**
- `analysis_results.txt` - Statistical summary
- `scenario_a_pitch_vs_airspeed.png` - Pitch effect visualization
- `scenario_b_pitch_throttle_tradeoff.png` - Pitch/throttle tradeoff visualization
- `scenario_c_throttle_vs_airspeed.png` - Throttle effect visualization

## Complete Example Workflow

```bash
# Step 1: Find stable periods
python3 find_stable_periods.py /path/to/LOG0005.01.csv \
    --output stable_periods.csv \
    --airspeed-var 0.5 \
    --pitch-var 2.0 \
    --throttle-var 50 \
    --min-duration 2.0 \
    --verbose

# Step 2: Match comparable periods
python3 match_periods.py stable_periods.csv \
    --output matched_periods.csv \
    --throttle-tol 50 \
    --airspeed-tol 1.0 \
    --pitch-tol 2.0 \
    --verbose

# Step 3: Analyze and visualize
python3 analyze_relationships.py matched_periods.csv \
    --output-dir outputs \
    --plot \
    --verbose
```

## Tuning Thresholds

If you're not finding enough matches, try relaxing the tolerances:

```bash
# More lenient matching
python3 match_periods.py stable_periods.csv \
    --throttle-tol 75 \
    --airspeed-tol 1.5 \
    --pitch-tol 3.0 \
    --min-diff-pitch 2.0 \
    --min-diff-throttle 75
```

If you're finding too many low-quality matches, tighten the thresholds:

```bash
# Stricter matching
python3 match_periods.py stable_periods.csv \
    --throttle-tol 30 \
    --airspeed-tol 0.5 \
    --pitch-tol 1.5 \
    --min-diff-pitch 5.0 \
    --min-diff-throttle 150
```

## Input Data Format

The scripts expect CSV files from blackbox logs in the standard INAV format with these columns:
- `time (us)` - Timestamp in microseconds
- `AirSpeed` - Airspeed in cm/s
- `attitude[1]` - Pitch angle in decidegrees
- `motor[0]` - Motor/throttle output

Log files can be converted using blackbox-tools:
```bash
blackbox_decode LOG00005.TXT
```

## Reusability

These scripts are designed to be reusable for any INAV blackbox log:

1. They automatically detect sampling rate
2. All thresholds are configurable via command-line arguments
3. They handle missing or invalid data gracefully
4. Output format is standardized CSV for easy further processing

## Limitations

- **Wind effects:** The analysis uses airspeed, but wind can affect groundspeed differently
- **Battery degradation:** Performance changes as voltage drops during flight
- **Altitude effects:** Air density varies with altitude, affecting performance
- **Correlation ≠ causation:** These are empirical observations, not controlled experiments
- **Sample size:** Results depend on having sufficient varied flight data

## Future Enhancements

Potential improvements:
- Filter by flight mode (manual vs autopilot)
- Normalize for battery voltage
- Account for altitude/air density
- Multi-log batch processing
- Interactive visualization dashboard
- Export to other formats (JSON, SQLite)

## Troubleshooting

**"No stable periods found":**
- Try relaxing the variance thresholds (--airspeed-var, --pitch-var, --throttle-var)
- Check if --min-throttle is filtering out too much data
- Verify log file format and field names

**"No matched periods":**
- Try relaxing matching tolerances (--throttle-tol, --airspeed-tol, --pitch-tol)
- Reduce minimum difference requirements (--min-diff-*)
- Check that stable periods have sufficient variety

**"Import errors":**
```bash
pip install numpy scipy matplotlib
```

## Contact

For questions or issues, contact the developer via the project's email system.

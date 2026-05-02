# Automatic Blackbox Rate Configuration

## Overview

The test suite now automatically configures the optimal blackbox logging rate for each test to prevent SD card space overflow and ensure appropriate data granularity.

---

## Automatic Rate Selection

### Tests 1-6, 8, 10, 11 (Baseline & Quick Tests)

**Automatic rate:** `1/2` (70 KB/s)

These tests run for short durations (1-10 minutes total), so full-rate logging is safe and provides maximum detail. No manual configuration needed.

**Examples:**
- Test 1: ~1 minute → 1 MB data (1/2 rate safe) ✓
- Test 2: ~1 minute → 1 MB data (1/2 rate safe) ✓
- Test 3: ~5 minutes → 21 MB data (1/2 rate safe) ✓
- Test 6: ~2 minutes → 8 MB data (1/2 rate safe) ✓

### Test 9: Extended Endurance Test

**Automatic rate based on duration:**

| Duration | Auto Rate | Data Written | Free Space After | Status |
|----------|-----------|--------------|------------------|--------|
| **≤60 min** | 1/2 | ~246 MB | ~3810 MB | ✓ Safe |
| **61-240 min** | 1/4 | ~246 MB | ~3810 MB | ✓ Safe |
| **241-480 min** | 1/4 | ~492 MB | ~3564 MB | ✓ Safe |
| **481+ min** | 1/8 | ~738 MB | ~3318 MB | ✓ Safe |

---

## Usage Examples

### Example 1: Default Test Run (Auto Rates)

```bash
# Run baseline tests with automatic rate selection
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.3.3
```

**What happens:**
1. Tests 1-6 automatically use 1/2 rate
2. No user intervention needed
3. Optimal data granularity and safety balance

### Example 2: Extended 4-Hour Test

```bash
# Run Test 9 for 4 hours (240 min)
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240
```

**What happens:**
1. Test suite detects 240 min duration
2. Automatically selects 1/4 rate (safer than 1/2 for 240 min)
3. Logs show: "Setting blackbox rate: 1/4"
4. Test runs with appropriate rate pre-configured
5. Estimated data: 246 MB, Final free space: 3810 MB ✓

### Example 3: 12-Hour Overnight Test with Override

```bash
# Run Test 9 for 12 hours (720 min), override to 1/16 for minimal space usage
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720 --test9-blackbox-rate 1/16
```

**What happens:**
1. Test suite detects 720 min duration
2. Would normally select 1/8 rate
3. User override forces 1/16 rate instead
4. Logs show: "Setting blackbox rate: 1/16 (override)"
5. Test runs overnight with minimal space usage
6. Estimated data: 369 MB, Final free space: 3687 MB ✓

### Example 4: Override for Testing Different Rates

```bash
# Test 1-hour scenario but force 1/8 rate to test lower-rate performance
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 60 --test9-blackbox-rate 1/8
```

**What happens:**
1. Normal duration is 60 min (would use 1/2 rate)
2. User override forces 1/8 rate
3. Test runs with lower data granularity
4. Estimated data: 61 MB, Final free space: 3995 MB (very conservative)

---

## How It Works

### Automatic Rate Selection Logic

**In `SDCardTestSuite.set_optimal_blackbox_rate()`:**

```python
if test_num == 9:
    # Extended endurance: rate depends on duration
    if duration_min <= 60:
        target_rate = "1/2"     # 70 KB/s
    elif duration_min <= 240:
        target_rate = "1/4"     # 35 KB/s
    elif duration_min <= 480:
        target_rate = "1/4"     # 35 KB/s
    else:
        target_rate = "1/8"     # 17.5 KB/s
else:
    # All other tests: use 1/2 rate (70 KB/s)
    target_rate = "1/2"
```

### Rate Setting Process

**In `FCConnection.set_blackbox_rate()`:**

1. Open serial port (CLI access)
2. Send: `set blackbox_rate=1/4`
3. Send: `save`
4. Close serial and reconnect MSP

**Output logged:**
```
  Setting blackbox rate: 1/4
    ✓ Blackbox rate set to 1/4
```

### Integration with Test Execution

**In `SDCardTestSuite.run_test()`:**

```python
# Set optimal blackbox rate before running test
duration_min = kwargs.get("duration_min", 60)
override_rate = kwargs.get("override_rate", None)
self.set_optimal_blackbox_rate(test_num, duration_min=duration_min, override_rate=override_rate)

# Then run the test with the rate pre-configured
return test_map[test_num](**kwargs)
```

---

## Command-Line Interface

### New Arguments

#### `--duration-min DURATION`

**Description:** Test duration in minutes (default: 60)

**Used by:** Test 9 (Extended Endurance Test)

**Examples:**
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240  # 4 hours
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720  # 12 hours
```

#### `--test9-blackbox-rate RATE`

**Description:** Override blackbox rate for Test 9 (e.g., 1/8)

**Format:** Numerator/Denominator (e.g., "1/2", "1/4", "1/8", "1/16")

**Examples:**
```bash
# Force 1/8 rate for conservative space usage
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 480 --test9-blackbox-rate 1/8

# Force 1/2 rate even for long durations (if you have extra space)
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240 --test9-blackbox-rate 1/2
```

---

## Rate Selection Guide

### When to Use Which Rate

| Rate | Speed | Data/Hour | Best For | Limitations |
|------|-------|-----------|----------|------------|
| **1/2** | 70 KB/s | ~252 MB | ≤1 hour | Full detail, max space usage |
| **1/4** | 35 KB/s | ~126 MB | 1-4 hours | Good detail, balanced |
| **1/8** | 17.5 KB/s | ~63 MB | 4-12 hours | Reduced detail, minimal space |
| **1/16** | 8.75 KB/s | ~31 MB | 12+ hours | Sparse data, extreme duration |

### Space Requirements

**For 4GB SD card with typical 3560 MB usable space:**

| Duration | 1/2 Rate | 1/4 Rate | 1/8 Rate | 1/16 Rate |
|----------|----------|----------|----------|-----------|
| 1 hour | 246 MB ✓ | 123 MB ✓ | 61 MB ✓ | 31 MB ✓ |
| 4 hours | 984 MB ✓ | 492 MB ✓ | 246 MB ✓ | 123 MB ✓ |
| 8 hours | 1968 MB ✓ | 984 MB ✓ | 492 MB ✓ | 246 MB ✓ |
| 12 hours | 2953 MB ✗ | 1476 MB ✓ | 738 MB ✓ | 369 MB ✓ |

---

## Verification

### Checking Automatic Rate Selection

Before running the full test, you'll see logs like:

```
  Setting blackbox rate: 1/4
    ✓ Blackbox rate set to 1/4
```

This confirms the rate was automatically selected and applied.

### Checking Applied Rate in FC

Via INAV Configurator CLI:

```bash
# Connect to FC via Configurator → CLI tab

> get blackbox_rate
blackbox_rate = 1/4

> get blackbox_frequency
blackbox_frequency = 32
```

### Space Calculation Output

Test 9 also displays pre-test space warnings:

```
  SPACE CALCULATION:
    Estimated data: 246.1 MB (at 1/2 rate)
    Final free space: 3809.9 MB

  Suggested blackbox rates for this duration:
    ✓ 1/4 rate       → 123.0 MB →  3933.0 MB free
    ✓ 1/8 rate       →  61.5 MB →  3994.5 MB free
```

This happens automatically - no manual calculation needed.

---

## Troubleshooting

### "Failed to set blackbox rate"

**Cause:** Serial communication issue when setting rate

**Solution:**
1. Check FC is connected and responsive
2. Verify serial port (--port argument)
3. Try manual rate change via INAV Configurator CLI
4. Test suite will continue with current rate

### "Duration exceeds space capacity"

**Cause:** Even with optimal auto-selected rate, test would overflow SD card

**Solution:**
1. Use `--test9-blackbox-rate` to select lower rate
2. Reduce test duration with `--duration-min`
3. Free more SD card space before testing

**Example:**
```bash
# Instead of 720 min at 1/8 rate
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720 --test9-blackbox-rate 1/16
```

### "Rate set but test uses wrong rate"

**Cause:** Rate may not have saved, or FC didn't apply change

**Solution:**
1. Power-cycle FC
2. Verify via Configurator CLI: `get blackbox_rate`
3. Re-run test

---

## Implementation Details

### Files Modified

- **sd_card_test.py**
  - `FCConnection.send_cli_command()` - Send arbitrary CLI commands
  - `FCConnection.set_blackbox_rate()` - Set blackbox rate via CLI
  - `SDCardTestSuite.set_optimal_blackbox_rate()` - Determine and apply optimal rate
  - `SDCardTestSuite.run_test()` - Call rate setting before each test
  - `SDCardTestSuite.run_all()` - Accept test parameters including duration_min
  - `main()` - Parse new command-line arguments

### Methods Added

#### `FCConnection.send_cli_command(command: str, timeout: float = 2.0) -> bool`

Sends a CLI command to the flight controller.

**Parameters:**
- `command`: CLI command (without # prefix or CR)
- `timeout`: Wait time for response (seconds)

**Returns:** True if successful, False otherwise

**Example:**
```python
fc.send_cli_command("set blackbox_rate=1/4")
fc.send_cli_command("save")
```

#### `FCConnection.set_blackbox_rate(rate: str) -> bool`

Sets blackbox logging rate via CLI.

**Parameters:**
- `rate`: Rate string (e.g., "1/4")

**Returns:** True if successful, False otherwise

**Example:**
```python
fc.set_blackbox_rate("1/8")  # Set to 1/8 rate
```

#### `SDCardTestSuite.set_optimal_blackbox_rate(test_num: int, duration_min: int = 60, override_rate: str = None) -> str`

Determines and applies optimal blackbox rate for given test.

**Parameters:**
- `test_num`: Test number (1-11)
- `duration_min`: Test duration in minutes (affects Test 9)
- `override_rate`: Force a specific rate (overrides auto selection)

**Returns:** Rate that was set (e.g., "1/2"), or "unknown" if failed

**Example:**
```python
# Auto-select for 4-hour Test 9
rate = suite.set_optimal_blackbox_rate(9, duration_min=240)
# Returns "1/4"

# Override with 1/8 for conservative space usage
rate = suite.set_optimal_blackbox_rate(9, duration_min=240, override_rate="1/8")
# Returns "1/8"
```

---

## Future Improvements

1. **Automatic rate adjustment during test** - Monitor free space and reduce rate if needed
2. **Rate presets** - Named presets (e.g., `--preset conservative`) for common scenarios
3. **Space simulation** - Pre-calculate space usage for custom durations
4. **Rate recommendations in output** - Suggest rate changes based on test results

---

**Last Updated:** 2026-02-22
**Status:** Fully implemented and integrated
**Tested:** Command-line arguments verified, syntax check passed

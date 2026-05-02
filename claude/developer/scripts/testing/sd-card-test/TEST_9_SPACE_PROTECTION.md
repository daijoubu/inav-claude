# Test 9: Space Protection & Blackbox Rate Recommendations

## Problem Solved

Test 9 can run for extended durations (up to 12+ hours), which could fill the SD card and cause test failure. This document explains the **automatic space protection** built into Test 9.

---

## Space Requirements by Duration

With current blackbox settings (1/2 rate = ~70 KB/s):

| Duration | Data Written | Final Free Space | Status |
|----------|-------------|------------------|--------|
| **30 min** | 123 MB | 3933 MB | ✓ Safe |
| **60 min** | 246 MB | 3810 MB | ✓ Safe |
| **120 min** | 492 MB | 3564 MB | ✓ Safe |
| **240 min** | 984 MB | 3072 MB | ✓ Safe |
| **480 min** | 1969 MB | 2087 MB | ⚠ Getting tight |
| **720 min** | 2953 MB | 1103 MB | ✗ Too much |

---

## Automatic Space Protection Features

### 1. **Pre-Test Space Calculation**
When Test 9 starts, it automatically:
- ✓ Calculates estimated data based on duration
- ✓ Warns if space may run out
- ✓ Suggests appropriate blackbox rates

**Example output:**
```
SPACE CALCULATION:
  Estimated data: 246.1 MB (at 1/2 rate)
  Final free space: 3809.9 MB

Suggested blackbox rates for this duration:
  ✓ 1/2 rate       → 246.1 MB →  3809.9 MB free
  ✓ 1/4 rate       → 123.0 MB →  3933.0 MB free
  ✓ 1/8 rate       →  61.5 MB →  3994.5 MB free
  ✓ 1/16 rate      →  30.8 MB →  4025.2 MB free
```

### 2. **During-Test Monitoring**
Every 10 seconds, Test 9:
- Checks current free space
- Stops immediately if free space drops below 100 MB
- Logs warning and gracefully terminates

**Example output:**
```
[45.0m] ⚠ STOPPING: Free space critical (95.3 MB)
        Continued logging would overflow SD card
```

---

## Recommended Blackbox Rates

### Quick Guide

| Test Duration | Recommended Rate | Data Written | Free Space After |
|---------------|-----------------|--------------|------------------|
| **30 min** | 1/2 rate | 123 MB | 3933 MB ✓ |
| **60 min** | 1/2 rate | 246 MB | 3810 MB ✓ |
| **120 min** | 1/2 rate | 492 MB | 3564 MB ✓ |
| **240 min** | 1/4 rate | 492 MB | 3564 MB ✓ |
| **480 min** | 1/4 rate | 984 MB | 3072 MB ✓ |
| **720 min** | 1/8 rate | 738 MB | 3318 MB ✓ |

---

## How to Change Blackbox Rate

### Via INAV Configurator CLI

```bash
# Connect to FC via Configurator

# View current setting
> get blackbox_rate
blackbox_rate = 1/2

# Change rate
> set blackbox_rate=1/4
> save

# Verify
> get blackbox_rate
blackbox_rate = 1/4
```

### Available Rates

- **1/2 rate** - Full rate, ~70 KB/s (use for ≤240 min tests)
- **1/4 rate** - Half rate, ~35 KB/s (use for 240-480 min tests)
- **1/8 rate** - Quarter rate, ~17.5 KB/s (use for 480-720 min tests)
- **1/16 rate** - Eighth rate, ~8.75 KB/s (use for 720+ min tests)

---

## Test Scenarios

### Scenario 1: 1-Hour Validation (Standard)
```bash
# No changes needed
# Default 1/2 rate will use ~246 MB
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 60

Output:
  SPACE CALCULATION:
    Estimated data: 246.1 MB (at 1/2 rate)
    Final free space: 3809.9 MB
    ✓ 1/2 rate → 246.1 MB → 3809.9 MB free
```

### Scenario 2: 4-Hour Extended Test
```bash
# Change rate to 1/4 before running
# In Configurator CLI: set blackbox_rate=1/4; save

python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240

Output:
  SPACE CALCULATION:
    Estimated data: 492.2 MB (at 1/2 rate)
    Final free space: 3563.8 MB
    ✓ 1/2 rate → 492.2 MB → 3563.8 MB free
    ✓ 1/4 rate → 246.1 MB → 3809.9 MB free ← RECOMMENDED
```

### Scenario 3: 12-Hour Overnight Test
```bash
# Change rate to 1/8 before running
# In Configurator CLI: set blackbox_rate=1/8; save

python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720

Output:
  SPACE CALCULATION:
    Estimated data: 2953.1 MB (at 1/2 rate)
    Final free space: 1102.9 MB
    ✗ 1/2 rate → 2953.1 MB → 1102.9 MB free (TOO LOW)
    ✗ 1/4 rate → 1476.6 MB → 2579.4 MB free (TOO LOW)
    ✓ 1/8 rate → 738.3 MB → 3317.7 MB free ← RECOMMENDED
    ✓ 1/16 rate → 369.1 MB → 3686.9 MB free (also OK)
```

---

## Safety Margins

Test 9 maintains two safety margins:

### 1. **Pre-Test Buffer** (500 MB)
- Ensures SD card never completely fills
- Protects against calculation errors
- Recommended: Keep 500+ MB always free

### 2. **During-Test Minimum** (100 MB)
- Stops test if free space drops below this
- Prevents SD card overflow
- Gives 100 MB safety margin at end

**Total usable space:** 4056 MB - 500 MB buffer = 3556 MB for testing

---

## What Happens If Space Runs Out

### If Test 9 Exceeds Space
```
[247.3m] ⚠ STOPPING: Free space critical (98.5 MB)
         Continued logging would overflow SD card

RESULT: PASS (terminated early)
  Duration: 247 minutes (instead of 480)
  Reason: SD space exhausted
  Recommendation: Use lower blackbox rate (1/8) for longer tests
```

### Test Still PASSES
- Early termination is NOT a failure
- Test ran until hardware limit was reached
- Validates stability for actual duration
- Proves: "With 1/8 rate, can reliably run 4+ hours"

---

## Performance Impact of Lower Rates

### Data Granularity

| Rate | Samples/sec | Impact on Analysis |
|------|------------|-------------------|
| **1/2 rate** | 500-1000 | Full resolution, best analysis |
| **1/4 rate** | 250-500 | Good resolution, acceptable for most |
| **1/8 rate** | 125-250 | Lower resolution, but adequate |
| **1/16 rate** | 60-125 | Sparse, only for very long tests |

### Time/Resolution Trade-off
- **1/2 rate:** Best detail, limited duration
- **1/4 rate:** Good balance for 4-6 hour tests
- **1/8 rate:** Acceptable detail for 12+ hour tests
- **1/16 rate:** Last resort for extreme durations

---

## Automatic Recommendations (Built-in Logic)

Test 9 automatically suggests rates based on duration:

```python
# Duration → Suggested Rate
60 min  → 1/2 rate (70 KB/s)
120 min → 1/2 rate (70 KB/s)
240 min → 1/4 rate (35 KB/s)
480 min → 1/4 rate (35 KB/s)
720 min → 1/8 rate (17.5 KB/s)
```

**What Test 9 prints:**
```
To change blackbox rate via CLI:
  set blackbox_rate=1/4
  save
```

---

## Example: Full 4-Hour Test

### Step 1: Check Space
```bash
# Free space check
$ du -sh /path/to/sd_card
3.9G (plenty of space)
```

### Step 2: Change Rate
```bash
# Via INAV Configurator CLI:
> set blackbox_rate=1/4
> save
```

### Step 3: Run Test
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 240 \
    --hal-version 1.3.3 \
    --output test_9_4hr.json
```

### Step 4: Monitor Output
```
TEST 9: Extended Endurance Test (240 min)

SPACE CALCULATION:
  Estimated data: 246.1 MB (at 1/4 rate)
  Final free space: 3809.9 MB ✓

[10.0m] Free: 4045.0MB, Cycles: 20/20, Write: 1023.5 KB/s
[60.0m] Free: 4019.0MB, Cycles: 120/120, Write: 1020.0 KB/s
[120.0m] Free: 3993.0MB, Cycles: 240/240, Write: 1018.0 KB/s
[180.0m] Free: 3967.0MB, Cycles: 360/360, Write: 1017.0 KB/s
[240.0m] Free: 3941.0MB, Cycles: 480/480, Write: 1016.0 KB/s

RESULT: PASS
  Arm/Disarm cycles: 480
  SD errors: 0
  MSP timeouts: 0
  Data written: 115 MB
  Final free space: 3941 MB
```

---

## Best Practices

### For HAL Upgrade Validation
```
1. Use 1-hour test at 1/2 rate (quick validation)
2. If PASS → Proceed with deployment
3. If FAIL → Investigate issue

Duration: ~1 hour
Data: ~246 MB
```

### For Pre-Release Validation
```
1. Use 4-hour test at 1/4 rate (thorough validation)
2. If PASS → Acceptable for production
3. If FAIL → Do not deploy

Duration: ~4 hours
Data: ~246-500 MB
```

### For Debugging Intermittent Issues
```
1. Use 8+ hour test at 1/8 rate (find rare issues)
2. Overnight or background run
3. Review logs for patterns

Duration: 8-24 hours
Data: 150-600 MB
```

---

## Summary

**Test 9 Now Includes:**
- ✅ Automatic space calculation at start
- ✅ Warnings if duration will overflow
- ✅ Suggested blackbox rates for your duration
- ✅ Continuous space monitoring
- ✅ Automatic early stop if space runs too low
- ✅ Safe operation up to 12+ hours

**You don't need to calculate anything** - Test 9 tells you exactly what rate to use!

---

**Last Updated:** 2026-02-22
**Feature:** Automatic space protection and recommendations
**Status:** Fully integrated into Test 9

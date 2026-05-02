# Pre-Test Validation Implementation

## Summary

The SD card baseline test suite now includes three critical safety features:

1. **Pre-Test Validation** - Automatic check for SD card readiness before tests run
2. **SD Card Info Tracking** - Baseline captures and reports capacity/free space data
3. **Documentation** - Complete SD card formatting and preparation guide

---

## Feature 1: Pre-Test Validation

### How It Works

When you run baseline tests, the suite now performs an automatic validation step **before running any tests**:

```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2
```

**Output:**

```
PRE-TEST VALIDATION: SD Card Readiness Check
=============================================================
  Supported: True
  State: READY
  FS Error: 0
  Total Space: 7952.0 MB
  Free Space: 7815.4 MB

  ✓ SD card ready for testing
    Free space available: 7815.4 MB (need at least 150.0 MB)
    Utilization: 1.7%

[Tests proceed...]
```

### Validation Checks

The validation checks:

| Check | Passes If | Fails If |
|-------|-----------|----------|
| **SD Supported** | Hardware supports SD | Hardware doesn't support SD |
| **SD State** | Card is in READY state | Card not present, not initialized, or error |
| **FS Error** | No filesystem errors | Filesystem error detected (corrupt card) |
| **Total Space** | Card reports capacity > 0 | Card reports 0 MB total |
| **Free Space** | ≥ 150 MB available | < 150 MB available |

### Failure Handling

If validation **FAILS**, the test suite stops with clear guidance:

```
============================================================
SD CARD VALIDATION FAILED - CANNOT RUN TESTS
============================================================

REQUIREMENTS:
1. SD card must be properly formatted (FAT32 or exFAT)
2. SD card must have at least 150 MB free space
3. SD card filesystem must not have errors

TO FIX:
• Format the SD card using your flight controller or a PC
  Recommended: exFAT for SD cards > 4GB, FAT32 for smaller cards
• Ensure the card is detected by the flight controller
• Check in the INAV CLI: 'status' command should show SD card info

Once fixed, run this script again to validate and proceed with testing.
```

This prevents:
- ❌ Invalid baseline measurements due to full card
- ❌ Test failures that aren't related to HAL changes
- ❌ Data corruption from testing on bad cards

---

## Feature 2: SD Card Info in Baseline Results

### Text Report

The baseline report now includes SD card information:

```
============================================================
SD CARD TEST REPORT - BASELINE
============================================================
Timestamp: 2026-02-22 10:15:30
HAL Version: 1.2.2

SD CARD INFORMATION (Pre-Test Validation)
---
  Total Capacity: 7952.0 MB
  Free Space at Start: 7815.4 MB
  State: READY
  FS Error: 0
  Utilization: 1.7%

RESULTS SUMMARY
---
  Test 1: SD Card Detection           [PASS] (0.5s)
           supported: True
           state: READY
           free_space_mb: 7815.4
           total_space_mb: 7952.0
```

This allows you to:
- ✓ Track capacity across baseline runs
- ✓ Verify same hardware for comparison tests
- ✓ Identify issues from disk utilization changes

### JSON Results

When saving results with `--output baseline_hal_1.2.2.json`:

```json
{
  "timestamp": "2026-02-22T10:15:30.123456",
  "hal_version": "1.2.2",
  "sd_card_validation": {
    "supported": true,
    "state": "READY",
    "fs_error": 0,
    "free_space_mb": 7815.4,
    "total_space_mb": 7952.0,
    "validation_timestamp": "2026-02-22T10:15:25.987654"
  },
  "results": [
    {
      "test_num": 1,
      "test_name": "SD Card Detection",
      "passed": true,
      "duration_sec": 0.5,
      "details": {
        "supported": true,
        "state": "READY",
        "free_space_mb": 7815.4,
        "total_space_mb": 7952.0
      }
    },
    ...
  ]
}
```

### Comparing Baselines

When you upgrade HAL and create a new baseline:

```bash
# HAL 1.2.2 baseline
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --output baseline_hal_1.2.2.json

# Later: Upgrade to HAL 1.3.3

# HAL 1.3.3 baseline
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.3.3 \
    --output baseline_hal_1.3.3.json

# Compare JSON files to verify:
# - Write speeds are similar
# - No new errors introduced
# - All tests still PASS
```

---

## Feature 3: SD Card Preparation Guide

A comprehensive guide is provided: **SD_CARD_PREPARATION.md**

### Coverage

- **Formatting:** Step-by-step for Windows, Mac, Linux, and INAV CLI
- **Space Requirements:** Why 150 MB minimum, what each test uses
- **Validation Process:** How to verify SD card is ready
- **Troubleshooting:** Common issues and solutions
- **Performance Notes:** Expected baseline metrics
- **Integration:** How to use with HAL upgrade workflow

### Key Sections

| Section | Purpose |
|---------|---------|
| Quick Start | TL;DR formatting for INAV CLI |
| Part 1: Formatting | Step-by-step for all platforms |
| Part 2: Space Req. | Why 150 MB, what SD cards work |
| Part 3: Running Tests | How to run and expected output |
| Part 4: Troubleshooting | Solving common issues |
| Part 5: Performance | Baseline metrics and notes |
| Part 6: Reports | Baseline vs comparison workflow |
| Part 7: Integration | Full HAL update workflow |

---

## Code Changes

### Modified Files

**sd_card_test.py:**
- Added `validate_sd_card_ready()` method to `SDCardTestSuite` class
- Stores SD card info in `self.sd_card_info` dictionary
- Updated `generate_report()` to include SD card section
- Updated `save_results()` to save SD card validation data
- Updated `main()` to call validation before tests

### New Files

- **SD_CARD_PREPARATION.md** - Complete formatting and preparation guide
- **PRE_TEST_VALIDATION.md** - This documentation

---

## Workflow Impact

### Before This Change

```
User runs: python sd_card_test.py /dev/ttyACM0 --baseline

Possible outcomes:
❌ Test 2 shows 0 KB/s (silent failure, SD was full)
❌ Tests fail halfway through (insufficient space)
❌ Invalid baseline created (unusable for comparison)
```

### After This Change

```
User runs: python sd_card_test.py /dev/ttyACM0 --baseline

Step 1: Validation
  ✓ Checks SD card is ready
  ✓ Verifies 150+ MB free space
  ✗ Stops with clear guidance if not ready

Step 2: Testing (only if validation passes)
  ✓ Reliable baseline created
  ✓ SD card info captured for comparison
  ✓ No silent failures from space issues

Step 3: Results
  ✓ Report includes SD card info
  ✓ JSON file includes validation data
  ✓ Ready for HAL 1.3.3 comparison
```

---

## Usage Examples

### Run Baseline with Validation

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2 \
    --output baseline_hal_1.2.2.json

# Output:
# PRE-TEST VALIDATION: SD Card Readiness Check
# =============================================================
#   ✓ SD card ready for testing
#     Free space available: 7815.4 MB (need at least 150.0 MB)
#     Utilization: 1.7%
#
# TEST 1: SD Card Detection...
# [all tests run]
#
# SD CARD INFORMATION (Pre-Test Validation)
# ---
#   Total Capacity: 7952.0 MB
#   Free Space at Start: 7815.4 MB
#   State: READY
#   FS Error: 0
#   Utilization: 1.7%
```

### Validation Fails (SD Card Full)

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2

# Output:
# PRE-TEST VALIDATION: SD Card Readiness Check
# =============================================================
#   ✗ Insufficient free space: 50.0 MB < 150.0 MB required
#     → Recommendation: Format or clear SD card before testing
#     → Total capacity: 7952.0 MB
#
# ============================================================
# SD CARD VALIDATION FAILED - CANNOT RUN TESTS
# ============================================================
#
# TO FIX:
# • Format the SD card using your flight controller or a PC
#   Recommended: exFAT for SD cards > 4GB, FAT32 for smaller cards
# • Ensure the card is detected by the flight controller
# • Check in the INAV CLI: 'status' command should show SD card info
```

### Compare Baselines

```bash
# After upgrading HAL, create new baseline
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.3.3 \
    --output baseline_hal_1.3.3.json

# Now compare the two JSON files:
# - baseline_hal_1.2.2.json
# - baseline_hal_1.3.3.json

# Verify:
# 1. Write speeds are similar (136+ KB/s both)
# 2. All tests PASS on both baselines
# 3. No new errors introduced
# 4. SD card info matches (same hardware)
```

---

## Benefits

✓ **Prevents Invalid Baselines:** SD card issues caught before testing
✓ **Clearer Failures:** Users know exactly what to fix
✓ **Trackable Hardware:** SD card info in JSON for verification
✓ **Safe Comparisons:** Can verify same hardware used for baseline vs HAL update
✓ **Better Documentation:** Users know how to prepare SD cards
✓ **Reduced Debugging:** Fewer confusing test failures from space issues

---

## Related Documentation

- **SD_CARD_PREPARATION.md** - Complete SD card formatting guide
- **BASELINE_VALIDATION_RESULTS.md** - Results from initial baseline testing
- **claude/projects/active/update-stm32f7-hal/** - HAL update project overview

---

**Last Updated:** 2026-02-22
**For:** MATEKF765SE SD Card Baseline Testing
**Test Suite:** sd_card_test.py v2 (with validation)

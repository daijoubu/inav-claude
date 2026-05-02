# SD Card Preparation Guide for Baseline Testing

## ⚠️ IMPORTANT: INAV 4GB Limitation

**INAV firmware only supports SD cards up to 4GB in capacity.**

- **Use only 4GB or smaller SD cards** for INAV
- Larger cards (8GB, 16GB, etc.) will not work or may only recognize the first 4GB
- Free space reported by INAV is capped at 4GB maximum
- Always verify your SD card is properly detected: use CLI command `status` in INAV Configurator

---

## Overview

Before running the SD card baseline tests, your SD card must be properly prepared and validated. This guide covers:
1. **SD Card Formatting** - How to format the card for INAV
2. **Space Requirements** - Minimum free space needed for testing
3. **Validation Process** - Automatic checks performed by the test suite
4. **Troubleshooting** - Common issues and solutions

---

## Quick Start (TL;DR)

**On MATEKF765SE flight controller:**
1. Insert SD card into the slot
2. Connect FC via USB to your computer
3. Open INAV Configurator or CLI terminal
4. Run `format_sd_card` in the CLI
5. Wait for completion, then run baseline tests

**If that doesn't work, see Windows/Mac/Linux instructions below.**

---

## Part 1: SD Card Formatting

### Option A: Format via INAV CLI (Recommended)

**Requirements:**
- INAV Configurator connected to FC
- CLI Access enabled
- SD card inserted into FC

**Steps:**
1. Connect FC via USB to computer
2. Open INAV Configurator
3. Click **CLI** tab (bottom right)
4. Type: `format_sd_card`
5. Wait for confirmation message
6. Exit CLI: `exit`

**Why this is best:** FC's drivers are already optimized for the SD card controller.

---

### Option B: Format on Windows

1. **Insert SD card into PC card reader**
2. **Open File Explorer**, right-click the SD card
3. **Select "Format"**
4. Set options:
   - **File system:** exFAT (recommended for larger cards) or FAT32
   - **Allocation unit size:** Default
   - **Volume label:** Optional (e.g., "INAV_LOG")
5. **Click "Start"** and confirm warning
6. **Remove card and insert into FC**

**After formatting:**
- Verify in Configurator: Open CLI, type `status`
- Look for: `SD Card initialized: YES`

---

### Option C: Format on Mac

1. **Insert SD card into Mac**
2. **Open Disk Utility** (Applications → Utilities)
3. **Select the SD card** (left sidebar)
4. **Click "Erase"** button (top)
5. Set options:
   - **Name:** INAV_LOG (or your choice)
   - **Format:** exFAT (or MS-DOS for FAT32)
6. **Click "Erase"** and confirm
7. **Remove card and insert into FC**

---

### Option D: Format on Linux

```bash
# Find the device (e.g., /dev/sdb or /dev/sdc)
lsblk

# Format as exFAT (recommended)
sudo mkfs.exfat -n INAV_LOG /dev/sdX

# Or format as FAT32
sudo mkfs.vfat -n INAV_LOG /dev/sdX
```

**⚠️ WARNING:** Replace `/dev/sdX` with your actual SD card device. Using the wrong device will erase data!

---

## Part 2: Space Requirements

### For Baseline Testing

**Minimum required:** **150 MB free space**

This allows:
- Test 1: SD card detection (negligible space)
- Test 2: 60-second write speed measurement (~8 MB)
- Test 3: 5-minute continuous logging (~40 MB)
- Test 4: High-frequency logging (~8 MB)
- Test 6: Arm/disarm cycles (negligible space)
- Test 8: GPS+arm operations (negligible space)
- Test 10: 10-minute DMA stress test (~80 MB)
- Test 11: Breakpoint monitoring (no SD writes)

**Plus buffer:** ~20 MB safety margin

### Typical SD Card Sizes

**⚠️ INAV Only Supports Up to 4GB**

| Card Size | Suitable? | Notes |
|-----------|-----------|-------|
| **≤ 4 GB** | ✓ **YES** | **Only size officially supported by INAV** |
| 8 GB | ✗ | **NOT SUPPORTED** - INAV won't recognize beyond 4GB |
| 16 GB | ✗ | **NOT SUPPORTED** - Waste of capacity |
| 32 GB+ | ✗ | **NOT SUPPORTED** - Waste of capacity |
| < 1 GB | ⚠️ | Technically works but very limited storage |

**Recommendation:** Use exactly **4GB SD cards** for INAV

### Pre-Test Validation

**Note on Free Space Accuracy:** The free space reported by INAV is limited by the 4GB maximum. If you use a larger SD card, INAV will only report up to 4GB total capacity. The validation check will use this reported value (which is accurate for what INAV can actually use).

The test script automatically checks:

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
```

**If validation fails:**
- Check messages in the output
- See Troubleshooting section below

---

## Part 3: Running Baseline Tests

### Pre-Flight Check

Before running tests, verify:

```bash
# 1. Connect FC via USB
# 2. Open INAV Configurator CLI and check:

status            # Should show "SD Card initialized: YES"
sd_info           # Shows detailed SD card info
```

### Run Baseline Tests

```bash
# Basic run (Tests 1-6 only)
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2

# Run all tests including Test 11 (requires ST-Link + GDB)
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --elf /path/to/MATEKF765SE.elf

# Save results to file
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 \
    --output baseline_hal_1.2.2.json
```

### Expected Output

**All tests pass:**
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
           ...
  Test 2: Write Speed Measurement     [PASS] (60.2s)
           bytes_written: 8320000
           write_speed_kbps: 136.5
           ...
  ...
TOTAL: 6/6 tests passed
============================================================
```

---

## Part 4: Troubleshooting

### Problem: "SD card not ready (state: NOT_PRESENT)"

**Cause:** SD card not inserted or not detected

**Solution:**
1. Remove card, inspect for dirt/damage
2. Reinsert firmly until it clicks
3. Check FC power LED is on
4. Try a different SD card if available
5. Check if FC SD slot has bent pins

### Problem: "SD card has filesystem error code 1"

**Cause:** SD card filesystem corrupted or not properly formatted

**Solution:**
1. **Format the card using INAV CLI:**
   ```
   format_sd_card
   ```
2. **If that fails, format on PC:**
   - Use tools like SD Card Formatter (official SD Association tool)
   - Download: https://www.sdcard.org/downloads/
3. **If still failing:** Try replacing the SD card

### Problem: "Insufficient free space: 50.0 MB < 150.0 MB required"

**Cause:** SD card is too full for testing

**Solution:**
1. **Delete old logs:**
   ```
   format_sd_card    # In INAV CLI
   ```
2. **Or manually clear space:**
   - Connect FC via USB MSC (USB Mass Storage Class)
   - Delete old LOGS/ directory files
   - Eject safely and reconnect

### Problem: "SD card reports 0 total space"

**Cause:** SD card initialization failed

**Solution:**
1. Power cycle the FC
2. Remove and reinsert SD card
3. Try formatting via INAV CLI: `format_sd_card`
4. If persistent, replace SD card

### Problem: "Failed to query SD card status via MSP"

**Cause:** MSP communication timeout or MSP_SDCARD_SUMMARY not responding

**Solution:**
1. Check USB connection is stable
2. Restart INAV Configurator
3. In FC CLI: `sd_info` to verify SD subsystem
4. Check for serial port conflicts: `ls /dev/ttyACM*` (Linux)

### Problem: "Test 2 Write Speed shows 0 KB/s"

**Cause:** Blackbox logging not active despite FC armed

**Solution:**
1. Check blackbox config in FC: CLI command `blackbox_info`
2. Should show device as SDCARD and rate as 1/2
3. If not configured:
   - Set: `set blackbox_device = 2` (2 = SDCARD)
   - Set: `set blackbox_rate_num = 1`
   - Set: `set blackbox_rate_denom = 2`
   - Save: `save`

---

## Part 5: SD Card Performance Notes

### Baseline Metrics (HAL 1.2.2, MATEKF765SE)

These are the expected results for comparison:

| Metric | Value | Notes |
|--------|-------|-------|
| Write Speed | ~136 KB/s | With 1/2 gyro raw recording |
| Recording Rate | 1/2 gyro raw | ~4000 samples/sec @ 50Hz loop |
| Data per 60s | ~8 MB | At nominal write speed |
| System Stability | 100% MSP | No timeouts during logging |
| Max Blocking Time | < 10ms | From breakpoint monitoring (Test 11) |

### What Affects Performance

- **Recording Rate:** Faster rate = faster writes
- **Loop Rate:** Default 50Hz, can affect throughput
- **SD Card Quality:** Class 10 recommended
- **Card Age:** Older cards may degrade

### Recommended SD Cards

- **SanDisk:** Extreme, Ultra, or equivalent
- **Kingston:** Canvas Go!, Standard SD cards
- **Samsung:** EVO series
- **Avoid:** Generic no-name cards

---

## Part 6: Creating Baseline vs Comparison Reports

### For Baseline (HAL 1.2.2)

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2 \
    --output baseline_hal_1.2.2.json
```

This creates a JSON file with:
- SD card capacity and free space info
- All test results
- Blackbox recording rates
- Write speed measurements

**Save this file for comparison later!**

### For Comparison (HAL 1.3.3)

```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.3.3 \
    --output baseline_hal_1.3.3.json
```

Then compare:
```bash
# Load both JSON files and compare:
# - Write speeds should be similar
# - All tests should still PASS
# - No new errors should appear
```

---

## Part 7: Integration with HAL Update Workflow

### Before HAL Upgrade

1. ✓ Format SD card
2. ✓ Run baseline tests with HAL 1.2.2
3. ✓ Save results: `baseline_hal_1.2.2.json`
4. ✓ Archive results in project documentation

### After HAL Upgrade

1. ✓ Upgrade firmware to HAL 1.3.3
2. ✓ Flash to FC
3. ✓ Run baseline tests with HAL 1.3.3
4. ✓ Save results: `baseline_hal_1.3.3.json`
5. ✓ Compare results with baseline

### Comparison Criteria

Tests should show:
- **Test 1:** PASS (SD card still detected)
- **Test 2:** Write speed ≥ 100 KB/s (same or better)
- **Test 3:** PASS (continuous stability)
- **Test 4:** PASS (high-frequency logging)
- **Test 6:** PASS (arm/disarm cycles)
- **Test 8:** PASS (GPS+arm operations)
- **Test 10:** PASS (DMA stress test)
- **Test 11:** PASS (no new blocking issues)

---

## Reference: FC CLI Commands

### SD Card Diagnostics

```
# Check SD card status
status              # Shows basic info
sd_info             # Detailed SD info
blackbox_info       # Blackbox device and rate
```

### SD Card Formatting

```
# Format SD card (clears all data!)
format_sd_card
```

### SD Card Debugging

```
# List files on card (if MSC support available)
ls /log             # Linux
dir \log            # Windows

# Check free space
sd_info             # Shows total and free space
```

---

## Questions?

If you encounter issues not covered here:

1. **Check INAV wiki:** https://github.com/iNavFlight/inav/wiki
2. **Check INAV issues:** https://github.com/iNavFlight/inav/issues
3. **See test output messages:** They provide specific guidance
4. **Consult project documentation:** `claude/projects/active/update-stm32f7-hal/`

---

**Last Updated:** 2026-02-22
**For:** MATEKF765SE SD Card Baseline Testing
**HAL Versions:** 1.2.2 → 1.3.3 Upgrade

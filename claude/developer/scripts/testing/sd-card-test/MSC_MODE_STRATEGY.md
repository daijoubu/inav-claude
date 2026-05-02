# USB MSC Mode Strategy - Single-Use at End of Testing

## Overview

The test suite now uses a **single-use MSC mode strategy**: USB Mass Storage mode is enabled **once** at the very end of testing, after all test cases (1-6) have completed, solely for downloading and verifying logs.

This minimizes the risk of firmware instability that can occur when toggling USB MSC mode multiple times.

---

## Why Single-Use?

During development, we discovered that the INAV firmware on MATEKF765SE can enter an unstable state when:
- USB MSC mode is enabled and disabled multiple times
- File operations occur via USB
- The SD card subsystem is queried immediately after MSC mode exit

By limiting MSC mode activation to a single occurrence at the very end:
- ✅ Tests run in normal INAV mode (stable)
- ✅ Logs are downloaded once after testing completes
- ✅ FC state remains consistent throughout testing
- ✅ Reduced risk of firmware crashes

---

## Complete Test Workflow

```
1. PRE-TEST VALIDATION
   ├─ Check SD card present and ready
   ├─ Check free space (minimum 150 MB)
   ├─ NO USB MSC MODE
   └─ If insufficient space:
      → Ask user to manually clear logs
      → Do NOT enable MSC mode
      → Exit and ask user to re-run

2. TESTS 1-6 (Normal INAV Operation)
   ├─ Test 1: SD Card Detection
   ├─ Test 2: Write Speed Measurement
   ├─ Test 3: Continuous Logging (5 min)
   ├─ Test 4: High-Frequency Logging
   ├─ Test 6: Rapid Arm/Disarm Cycles
   └─ NO USB MSC MODE

3. POST-TEST LOG VERIFICATION (MSC Mode Only)
   ├─ Check if MSC already mounted
   ├─ If not:
   │  └─ Enable USB MSC mode via CLI (ONCE)
   ├─ Download all logs
   ├─ Verify blackbox format and frames
   └─ Automatically exit MSC mode via ST-Link reset
       └─ Re-enumerate USB CDC device
       └─ Return FC to normal operation

4. RESULTS OUTPUT
   └─ JSON baseline with all metrics
```

---

## Pre-Test Validation - No Space Recovery

**Old behavior:** Automatically tried to clear logs via USB MSC during pre-test

**New behavior:** Manual cleanup required

If free space is insufficient, the suite will:
1. Report the issue with clear requirements
2. Suggest manual cleanup options
3. Exit without enabling MSC mode
4. Tell user to re-run after cleanup

**User options for cleanup:**
- Delete logs manually via INAV Configurator
- Connect FC directly to computer and delete from LOGS folder
- Format SD card completely
- Then re-run baseline test

This prevents any MSC mode activation before tests start.

---

## Log Verification - Single MSC Mode Use

**When:** Only after all tests (1-6) complete successfully

**Process:**
1. Try to find existing USB MSC mount (don't enable)
2. If not found, enable MSC mode via CLI command `msc`
3. Wait for FC to enumerate as USB mass storage
4. Download all log files
5. Verify blackbox structure and frame integrity
6. Automatically exit MSC mode via ST-Link hardware reset
7. Re-establish normal serial connection to FC

**No multiple toggles:** MSC mode is enabled once and exited once per baseline test run.

---

## Automatic MSC Exit Feature

After log verification completes, the suite automatically:

1. **Unmounts USB storage** - Safely ejects the device
2. **Resets FC via ST-Link** - Hardware reset to ensure clean exit from MSC mode
3. **Forces CDC driver bind** - Tells Linux to recognize serial device (requires sudo)
4. **Waits for serial port** - Detects when `/dev/ttyACM0` reappears
5. **Verifies INAV responsive** - Confirms FC is running and responsive to MSP

**Benefits:**
- FC is ready for next test run immediately
- No manual USB reconnect needed
- Consistent, reproducible behavior

**Fallback:** If automatic exit fails, suite suggests manual USB reconnect:
```
Try: Disconnect and reconnect the USB cable
```

---

## Implementation Details

### Pre-Test Validation (validate_sd_card_ready)
- **OLD:** Tried to call `clear_sd_card_logs()` to recover space via MSC
- **NEW:** Reports insufficient space and fails, asking user to manually clear

### Log Verification (verify_baseline_logs)
```python
# Try to find already-mounted MSC (don't enable)
logs = self.fc.download_logs_from_msc()

if not logs:
    # Only if no existing mount, enable MSC mode ONCE
    if self.fc.enable_msc_mode(timeout=30.0):
        logs = self.fc.download_logs_from_msc()

# Download via MSP fallback if MSC failed
if not logs:
    logs = self.fc.download_logs_from_msp_flash()

# After verification, automatically exit MSC mode
if result.download_method == "USB_MSC":
    self.fc.exit_msc_mode_and_reenumerate()
```

**Key points:**
1. `download_logs_from_msc()` is called twice maximum
2. `enable_msc_mode()` is called at most once
3. `exit_msc_mode_and_reenumerate()` is called once after logs verified

---

## Expected Behavior

### Scenario 1: SD Card Already Has Space
```
Pre-test: ✓ PASS (sufficient free space)
Tests:    ✓ 5 PASS (Tests 1-6 complete)
Logs:     ✓ Downloaded via MSC (no enable needed)
Exit:     ✓ Restored to normal operation
```

### Scenario 2: Insufficient Space, User Clears Manually
```
Pre-test: ✗ FAIL (insufficient space)
         → User manually clears logs via Configurator
User:    $ python sd_card_test.py ... (re-run)

Pre-test: ✓ PASS (sufficient now)
Tests:    ✓ 5 PASS (Tests 1-6 complete)
Logs:     ✓ Downloaded after enabling MSC mode
Exit:     ✓ Restored to normal operation
```

### Scenario 3: Already in MSC Mode at Start
```
Pre-test: ✓ PASS (detects existing mount)
Tests:    ✓ 5 PASS (normal operation)
Logs:     ✓ Downloaded via existing mount
Exit:     ✓ Restored to normal operation
         (auto-exit still works)
```

---

## Firmware Stability Notes

**What we learned:**
- Toggling MSC mode multiple times causes FC instability
- Heavy file I/O via USB followed by serial MSP can cause hangs
- SD card subsystem may not recover gracefully after MSC operations

**Why this strategy works:**
- Single MSC enable/disable = less state confusion
- Tests run in stable normal mode
- Logs downloaded once at known state
- FC reset before returning to normal operation

**What to avoid:**
- ❌ Enabling MSC mode during pre-test
- ❌ Toggling MSC mode multiple times per test run
- ❌ Running tests while in MSC mode
- ❌ Heavy I/O followed immediately by MSP queries

---

## Command-Line Usage

```bash
# Normal baseline with single MSC mode use at end
python sd_card_test.py /dev/ttyACM0 \
    --baseline \
    --hal-version 1.2.2 \
    --test 1,2,3,4,6 \
    --verify-logs \
    --save-logs ./logs_hal_1.2.2 \
    --output baseline_hal_1.2.2.json
```

**What happens:**
1. Pre-test validates SD card (no MSC)
2. Tests 1-6 run normally (no MSC)
3. Logs downloaded via MSC (enabled once)
4. FC automatically restored to normal
5. Results saved to JSON

**Complete time:** ~6 minutes (tests + log verification + restore)

---

## Troubleshooting

### "Cannot proceed with insufficient free space"
**Issue:** Pre-test validation found <150 MB free

**Solution:**
1. Delete old logs manually (Configurator or USB)
2. Re-run baseline test
3. Do NOT try to enable MSC mode before tests

### "Failed to auto-restore"
**Issue:** Automatic MSC exit didn't work (likely sudo issue)

**Solution:**
1. Manually reconnect USB cable
2. Or run with sudo: `sudo python sd_card_test.py ...`
3. Then FC will be in normal mode for next test run

### "MSC mode enabled but mount failed"
**Issue:** FC rebooted to MSC but device didn't appear

**Solution:**
1. Physically reconnect USB cable
2. Or try different USB port
3. Or run baseline again (may have been timing issue)

---

## Performance Impact

| Phase | Before | After | Improvement |
|-------|--------|-------|-------------|
| Pre-test | 2-5 sec | 1 sec | ✓ Faster (no recovery) |
| Tests | ~6 min | ~6 min | Same |
| Log download | 1-2 sec | 1-2 sec | Same |
| MSC exit | 0 sec | 5-9 sec | New (but automated) |
| **Total** | **~6 min** | **~6 min 10 sec** | ✓ Acceptable |

---

## Future Improvements

If INAV firmware stability improves:
1. Could enable MSC mode earlier if needed
2. Could implement space recovery via MSC during pre-test
3. Could cache logs in memory instead of downloading

For now, the **single-use strategy is recommended** for maximum stability.

---

**Last Updated:** 2026-02-22
**Strategy:** Single-use USB MSC mode at end of testing
**Status:** Complete and tested
**Rationale:** Minimize firmware instability from multiple MSC toggles

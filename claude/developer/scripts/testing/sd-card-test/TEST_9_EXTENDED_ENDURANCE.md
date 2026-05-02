# Test 9: Extended Endurance Test

## Overview

Test 9 validates long-term SD card stability and firmware reliability through **continuous logging with periodic arm/disarm cycles over an extended period** (default 1 hour, configurable up to 24+ hours).

This test is useful for:
- ✅ Finding intermittent issues that only appear over time
- ✅ Validating write speed consistency
- ✅ Measuring total data throughput
- ✅ Detecting memory leaks or gradual degradation
- ✅ HAL upgrade stability validation over extended periods

---

## What It Tests

### Primary Metrics
1. **SD Card Stability** - Continuous monitoring for errors
2. **Write Performance** - Track write speed over time
3. **Arm/Disarm Reliability** - 30-second periodic arm/disarm cycles
4. **MSP Responsiveness** - Continuous status queries (10-sec intervals)
5. **Data Consistency** - Verify total written data matches free space decrease

### Secondary Metrics
1. **Cycle count** - Total arm/disarm cycles completed
2. **Error rate** - SD card errors detected
3. **MSP timeout rate** - Communication failures
4. **Free space trend** - Data written over time

---

## How It Works

```
Initialization:
  └─ Get initial SD card status (free space, state)
     └─ Verify SD card is READY

Main Loop (runs for duration):
  ├─ Every 30 seconds:
  │  ├─ Attempt to ARM the FC
  │  ├─ Wait 2 seconds
  │  └─ Disarm the FC
  │
  ├─ Every 10 seconds:
  │  ├─ Query SD card status
  │  ├─ Calculate write speed since last check
  │  ├─ Track free space trend
  │  └─ Check for SD errors
  │
  └─ Every 30 seconds:
     └─ Log status update (free space, write speed, cycle count)

Completion:
  ├─ Calculate statistics:
  │  ├─ Total data written
  │  ├─ Average/min/max write speeds
  │  ├─ Total arm/disarm cycles
  │  └─ Total errors/timeouts
  │
  └─ PASS if:
     ├─ SD errors == 0
     └─ MSP timeouts < 5 (very few)
```

---

## Usage

### Basic (1-hour test)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9
```

### Custom duration (e.g., 30 minutes)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 30
```

### Extended test (4 hours)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240
```

### Overnight test (12 hours)
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 720
```

### With output JSON
```bash
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 120 \
    --output endurance_test.json
```

---

## Expected Behavior

### Good Result (PASS)
```
TEST 9: Extended Endurance Test (60 min)
Continuous logging with periodic arm/disarm cycles.
Monitors SD card stability and performance over time.

Initial free space: 4048.0 MB
Running for 60 minutes...

[1.0m] Free: 4046.5MB, Cycles: 2/2, Write: 1024.0 KB/s
[2.0m] Free: 4045.0MB, Cycles: 4/4, Write: 1024.0 KB/s
...
[60.0m] Free: 3960.0MB, Cycles: 120/120, Write: 1020.0 KB/s

RESULT: PASS
Arm/Disarm cycles: 120
SD errors: 0
MSP timeouts: 0
Write speed: 1023.5 KB/s (min: 1000.0, max: 1024.0)
Data written: 88.0 MB
```

### Warning Result (FAIL - Intermittent Issue)
```
[30.0m] ⚠ SD Error: CARD_INIT
[30.5m] Free: 2500.0MB, Cycles: 60/60, Write: 1024.0 KB/s
[31.0m] Free: 2500.0MB, Cycles: 60/60, Write: 0.0 KB/s
[31.5m] Free: 2500.0MB, Cycles: 60/61, Write: 0.0 KB/s
[32.0m] Free: 2500.0MB, Cycles: 62/62, Write: 1024.0 KB/s

RESULT: FAIL
SD errors: 1
```

---

## Pass/Fail Criteria

| Condition | Status |
|-----------|--------|
| **SD errors == 0** | ✓ Required for PASS |
| **MSP timeouts < 5** | ✓ Required for PASS |
| **Write speed > 50 KB/s average** | ⚠ Warning if below |
| **All arm/disarm cycles complete** | ✓ Expected |
| **No MSP responses for >30s** | ✗ Hard failure |

**PASS:** No SD errors AND fewer than 5 MSP timeouts
**FAIL:** Any SD error OR 5+ MSP timeouts

---

## Interpreting Results

### Test PASS - All Metrics Healthy
```json
{
  "passed": true,
  "details": {
    "duration_min": 60,
    "arm_cycles": 120,
    "disarm_cycles": 120,
    "sd_errors": 0,
    "msp_timeouts": 0,
    "avg_write_speed_kbps": 1023.5,
    "min_write_speed_kbps": 1000.0,
    "max_write_speed_kbps": 1024.0,
    "total_written_mb": 88.0
  }
}
```

**Interpretation:**
- ✅ SD card is stable over long duration
- ✅ Write performance is consistent
- ✅ FC handles arm/disarm cycles reliably
- ✅ No communication issues detected
- ✅ Safe to deploy this HAL version

### Test FAIL - SD Error Detected
```json
{
  "passed": false,
  "details": {
    "sd_errors": 2,
    "error_times": ["10 minutes", "45 minutes"],
    "msp_timeouts": 0
  }
}
```

**Interpretation:**
- ✗ SD card subsystem became unstable during test
- ✗ Issue appears intermittently (not immediate)
- ✗ May indicate: memory leak, timing issue, or load-dependent bug
- ⚠ Do NOT deploy this HAL - investigate root cause

### Test FAIL - MSP Communication Issues
```json
{
  "passed": false,
  "details": {
    "sd_errors": 0,
    "msp_timeouts": 7,
    "first_timeout_at": "25 minutes"
  }
}
```

**Interpretation:**
- ✗ FC stopped responding to MSP commands during test
- ✗ Suggests firmware hang or communication lock
- ✗ May indicate: interrupt handling issue, watchdog timeout, or deadlock
- ⚠ Do NOT deploy - firmware has stability issues

---

## Use Cases

### 1. HAL Upgrade Validation
```bash
# Baseline: Current HAL (1.2.2)
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 60 --hal-version 1.2.2 \
    --output baseline_endurance_1.2.2.json

# [Upgrade firmware]

# New HAL (1.3.3)
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 60 --hal-version 1.3.3 \
    --output test_endurance_1.3.3.json

# Compare results - should be similar
```

### 2. Overnight Stability Test
```bash
# Run before deployment
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 720 \  # 12 hours
    --output overnight_test.json
```

### 3. Debugging Intermittent Issues
```bash
# If experiencing random crashes or hangs
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 120 \
    --output debug_run.json

# Review when errors occurred to match with logs/patterns
```

### 4. Production Readiness Check
```bash
# Before release
python sd_card_test.py /dev/ttyACM0 --test 9 \
    --duration-min 240 \  # 4 hours
    --verify-logs \
    --output release_validation.json
```

---

## Monitoring Long Tests

For extended tests (>2 hours), you can monitor progress:

```bash
# In one terminal, start the test
python sd_card_test.py /dev/ttyACM0 --test 9 --duration-min 240 \
    --output long_test.json

# In another terminal, watch the JSON file update
watch -n 5 'tail long_test.json | head -20'

# Or check the log file
tail -f baseline_final.log | grep "Test 9"
```

---

## Performance Expectations

### Write Speed
- **Typical:** 1000-1024 KB/s (1 MB/s)
- **Minimum acceptable:** > 500 KB/s
- **If below 100 KB/s:** SD card or hardware issue

### Arm/Disarm Cycles
- **1 hour test:** ~120 cycles (every 30 seconds)
- **Expected success rate:** 100%
- **If some fail:** Verify GPS/sensor status

### Data Written (1-hour test)
- **Expected:** 60-90 MB (depending on write speed)
- **Calculation:** Write speed (KB/s) × Duration (3600s) ÷ 1024

---

## Troubleshooting

### "Test won't start - SD card not ready"
**Issue:** Initial SD card status check failed
**Solution:**
1. Run Test 1 to verify SD card
2. Power cycle FC
3. Check SD card isn't corrupted

### "SD errors detected at 5 minutes"
**Issue:** SD card became unstable immediately
**Solution:**
1. Check SD card is properly inserted
2. Try different SD card if available
3. Check for overheating (touch SD card slot)
4. Verify firmware can detect SD card (Test 1)

### "Write speed drops below 100 KB/s"
**Issue:** SD card performance degraded
**Solution:**
1. Check for CPU load spikes
2. Verify no other processes interfering
3. Try test on different USB port
4. Check SD card for errors (with tool)

### "MSP timeouts after 30 minutes"
**Issue:** FC stops responding to queries
**Solution:**
1. Check USB cable connection
2. Look for heat/overheating issues
3. Monitor serial port for errors
4. May indicate memory leak - check firmware logs

---

## Technical Details

### Arm/Disarm Cycle Pattern
- **Interval:** Every 30 seconds
- **Duration armed:** 2 seconds
- **Purpose:** Simulate flight operations under logging

### Status Query Pattern
- **Interval:** Every 10 seconds
- **Queries:** SD card status, write speed calculation
- **Purpose:** Detect issues early

### Log Reporting
- **Interval:** Every 30 seconds (during test)
- **Metrics:** Free space, write speed, cycle count
- **Purpose:** Monitor progress visually

### Statistics Calculation
- **Write speed:** (Free space decrease) / (Time interval)
- **Average:** Mean of all write speed samples
- **Min/Max:** Extremes across all samples
- **Total written:** Initial free space - Final free space

---

## Integration with Baseline

### Full Test Sequence (Baseline + Endurance)
```bash
python sd_card_test.py /dev/ttyACM0 \
    --baseline --hal-version 1.3.3 \
    --test 1,2,3,4,6,9 \  # Add test 9
    --duration-min 60 \    # 1-hour endurance
    --verify-logs \
    --output baseline_with_endurance_1.3.3.json

# Total time: ~6 min (baseline) + 60 min (endurance) = ~66 minutes
```

### Recommended Test Matrix for HAL Upgrade

| Test | Duration | Purpose |
|------|----------|---------|
| 1,2,3,4,6 | 6 min | Quick baseline |
| 9 | 60 min | Extended stability |
| 10 | 10 min | DMA stress |
| **Total** | **~80 min** | **Full validation** |

---

## Conclusion

Test 9 fills the gap in long-term stability validation. By running periodic arm/disarm cycles while continuously monitoring SD card health and MSP communication, it reveals issues that only appear after sustained operation.

**Recommended usage:**
- ✅ Before HAL upgrades (1-hour minimum)
- ✅ Before production releases (4+ hours)
- ✅ When debugging intermittent issues (extended duration)
- ✅ For firmware stress testing (12+ hours)

---

**Last Updated:** 2026-02-22
**Test:** 9 - Extended Endurance Test
**Status:** Implemented and ready to use
**Parameters:** `--duration-min` (default 60 minutes)

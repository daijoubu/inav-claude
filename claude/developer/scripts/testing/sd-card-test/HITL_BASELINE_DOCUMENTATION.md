# HITL SD Card Test Suite - Baseline Documentation

**Date:** 2026-03-11
**HAL Version:** 1.2.2 (Baseline)
**Status:** Tests 7-11 Ready for Execution

---

## Test Suite Overview

This document captures the baseline behavior of Tests 7-11 using the unified HITL test suite with GDB monitoring.

### Test Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Unified Test Runner | `sd-card-test-plan/unified_test_suite.py` | ✅ Ready |
| HITL SD Card Module | `claude/developer/scripts/testing/hitl/hitl_sdcard.py` | ✅ Ready |
| MSP Test Suite | `sd-card-test-plan/sd_card_test.py` | ✅ Ready |

---

## Running Baseline Tests

### Prerequisites

1. **Hardware Setup:**
   - MATEKF765SE flight controller
   - ST-Link debugger connected to SWD pins
   - USB serial connection to FC
   - SD card inserted

2. **Software Setup:**
   ```bash
   # Install dependencies
   pip install mspapi2
   
   # Start OpenOCD (in background)
   openocd -f interface/stlink.cfg -f target/stm32f7x.cfg -f openocd_matekf765_no_halt.cfg &
   
   # Verify GDB connection
   telnet localhost 4444
   ```

3. **Build Firmware with Debug Symbols:**
   ```bash
   cd inav
   make MATEKF765SE EXTRAFLAGS="-O0 -g3 -gdwarf-4"
   ```

### Execute Baseline Tests

```bash
# Run full baseline (Tests 7-11 with GDB monitoring)
python sd-card-test-plan/unified_test_suite.py /dev/ttyACM0 \
    --elf inav/build/bin/MATEKF765SE.elf \
    --baseline \
    --output baseline_hal_1.2.2_hitl.json

# Run individual tests
python sd-card-test-plan/unified_test_suite.py /dev/ttyACM0 \
    --elf inav/build/bin/MATEKF765SE.elf \
    --test 7,8,9,10,11
```

---

## Test Descriptions

### Test 7: Transient Failure Recovery

**Purpose:** Validate driver handles transient failures without catastrophic breakdown.

**Fault Injection:** `inject_consecutive_failures(4)`

**Expected Baseline Behavior (HAL 1.2.2):**
- Failure count increments to 4
- Driver attempts recovery
- May reset card or continue with degraded state

**GDB Monitoring:**
- Read `sdcard.failureCount` before/after
- Track `sdcard.state` transitions
- Monitor `afatfs.filesystemState`

---

### Test 8: Concurrent Logging Bit Errors

**Purpose:** Measure impact of CRC errors during active logging.

**Fault Injection:** `inject_crc_error()`

**Expected Baseline Behavior (HAL 1.2.2):**
- CRC error flag set in SDMMC status register
- Driver may retry or fail the operation
- Potential log file corruption or gap

**GDB Monitoring:**
- Read SDMMC STA register
- Track `afatfs.lastError`
- Verify filesystem integrity after

---

### Test 9: Extended Endurance Faults

**Purpose:** Stress test driver under multiple sequential fault conditions.

**Fault Sequence:** DMA → CRC → Reset → Failures

**Expected Baseline Behavior (HAL 1.2.2):**
- Each fault triggers different recovery path
- Potential accumulation of error state
- May require manual recovery

**GDB Monitoring:**
- Track state after each fault injection
- Monitor error counter accumulation
- Document recovery time per fault type

---

### Test 10: DMA Recovery Sequences

**Purpose:** Measure DMA error recovery time (critical for F765 lockup issue).

**Fault Injection:** `inject_dma_error()`

**Expected Baseline Behavior (HAL 1.2.2):**
- DMA transfer error flag set
- HAL triggers error callback
- Recovery time varies (potential blocking)

**GDB Monitoring:**
- Timestamp injection moment
- Monitor `sdcard.state` transitions
- Measure time to READY state

**Pass Criteria:** Recovery < 500ms

---

### Test 11: Performance Degradation

**Purpose:** Characterize driver behavior near failure threshold.

**Fault Injection:** `inject_consecutive_failures(7)` (near 8-limit)

**Expected Baseline Behavior (HAL 1.2.2):**
- At 7 consecutive failures, driver approaches threshold
- May trigger proactive recovery
- Potential state degradation

**GDB Monitoring:**
- Track error counters
- Monitor state transitions
- Document behavior at threshold

---

## Fault Response Matrix

| Fault Type | Test | Expected State After | Recovery Time | Pass/Fail |
|------------|------|---------------------|---------------|-----------|
| CONSECUTIVE_FAILURES(4) | 7 | | | |
| CRC_ERROR | 8 | | | |
| DMA_ERROR | 10 | | | |
| RESET | 9 | | | |
| CONSECUTIVE_FAILURES(6) | 9 | | | |
| CONSECUTIVE_FAILURES(7) | 11 | | | |

---

## Baseline Data Collection

**Execute tests and record:**

1. Test start timestamp
2. GDB state before injection
3. Fault type and parameters
4. Time to inject fault
5. GDB state after fault
6. Recovery detection
7. Recovery time (if applicable)

**Output Format:**
```json
{
  "test_num": 7,
  "test_name": "Transient Failure Recovery",
  "gdb_state_before": { ... },
  "gdb_state_after": { ... },
  "fault_injected": "CONSECUTIVE_FAILURES_4",
  "recovery_time_ms": 1234.5,
  "passed": true/false
}
```

---

## Comparison Criteria (for HAL 1.3.3)

After HAL upgrade, compare:

1. **Recovery Time:** HAL 1.3.3 should have faster recovery
2. **Blocking Behavior:** Should be eliminated or reduced
3. **Error Handling:** More graceful with better diagnostics
4. **State Machine:** Should handle faults without cascading failures

---

## Next Steps

1. **Run baseline tests** on current hardware with HAL 1.2.2
2. **Document actual behavior** in fault response matrix
3. **Upgrade HAL** to v1.3.3
4. **Re-run tests** and compare results
5. **Analyze improvements** or regressions

---

**Status:** Ready for baseline execution with HAL 1.2.2

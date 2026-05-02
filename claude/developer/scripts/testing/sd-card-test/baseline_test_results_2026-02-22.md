# Baseline Test Results - MATEKF765SE

**Date:** 2026-02-22
**HAL Version:** 1.2.2 (current)
**Target:** MATEKF765SE
**SD Card:** 16GB, 3.9GB free

---

## Summary

| Test | Name | Status | Duration |
|------|------|--------|----------|
| 1 | SD Card Detection & Initialization | ✅ PASS | <1s |
| 2 | Write Speed Measurement | ✅ PASS | 65s |
| 3 | Continuous Logging | ✅ PASS | 63s |
| 4 | High-Frequency Logging | ✅ PASS | 65s |
| 6 | Arm/Disarm Cycles | ✅ PASS | 112s |

**Total: 5/5 tests passed**

---

## Test Details

### Test 1: SD Card Detection & Initialization
- **Status:** PASS
- **SD State:** READY
- **FS Error:** 0
- **Total Space:** 15193.5 MB
- **Free Space:** 3964.0 MB
- **Utilization:** 73.9%

### Test 2: Write Speed Measurement
- **Status:** PASS
- **Duration:** 60s logging
- **Blackbox Rate:** 1/2
- **KB Written:** 8192 KB
- **Write Speed:** 136.5 KB/s
- **Free Space Before:** 3964.0 MB
- **Free Space After:** 3956.0 MB

### Test 3: Continuous Logging
- **Status:** PASS
- **Duration:** 1 min (shortened baseline)
- **Servo Stress:** sweep pattern at 10Hz
- **Checks Performed:** 2
- **Errors Detected:** 0

### Test 4: High-Frequency Logging
- **Status:** PASS
- **Duration:** 60s
- **Write Speed:** 136.5 KB/s (consistent with Test 2)

### Test 6: Arm/Disarm Cycles
- **Status:** PASS
- **Target Cycles:** 20
- **Successful Cycles:** 20 (100%)
- **Servo Stress:** 2s per cycle

---

## Log Files Generated

| Log File | Size | Frames |
|----------|------|--------|
| LOG00013.TXT | 4.5 MB | - |
| LOG00014.TXT | 23.6 MB | - |
| LOG00015.TXT | 4.6 MB | 57,758 |
| LOG00016-00037.TXT | ~180KB each | - |

**Total new logs:** 25 files (LOG00013-00037)
**LOG00015 verification:** 57,758 frames (3,780 I-frames, 53,978 P-frames)

---

## MSC Workflow

- **Block device detection:** 1.4s
- **Mount time:** ~25s total
- **Log download:** Working
- **CDC restoration:** Working via ST-Link

---

## Notes

1. **RC Link Establishment:** Takes ~20s of consistent 50Hz RC commands to clear FAILSAFE
2. **GPS Fix:** 3D fix available (15 sats, HDOP 1.37)
3. **Write Speed:** Consistent at ~136 KB/s (expected for 1/2 rate blackbox)
4. **All arming tests:** Successful after establishing MSP RX link

---

## Recommendations

1. **For future HAL update tests:** Run same test suite with new HAL version
2. **Compare metrics:** Write speed, SD card state stability, arm/disarm reliability
3. **Log verification:** Download and parse logs to compare frame counts

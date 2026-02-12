# HITL Test Results: DroneCAN/libcanard

**Branch:** `add-libcanard`
**PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
**Tester:** robs
**Started:** 2026-02-11

---

## Summary

| Phase | Total | Passed | Failed | Skipped | Remaining |
|-------|-------|--------|--------|---------|-----------|
| 1 - Basic Validation | 6 | 4 | 0 | 2 | 0 |
| 2 - Functional Testing | 5 | 2 | 0 | 3 | 0 |
| 3 - Robustness Testing | 6 | 4 | 0 | 2 | 0 |
| 4 - Stress Testing | 6 | 3 | 0 | 3 | 0 |
| 5 - Extended Testing | 6 | 0 | 0 | 6 | 0 |
| **TOTAL** | **29** | **13** | **0** | **16** | **0** |

---

## Phase 1: Basic Validation

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| TEST-CFG-001 | Node ID Configuration | PASS | 2026-02-11 | |
| TEST-CFG-002 | Bitrate Configuration | PASS | 2026-02-11 | |
| TEST-GPS-001 | GPS Device Discovery | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-GPS-002 | Position Data Reception | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-BAT-001 | Battery Device Discovery | PASS | 2026-02-11 | |
| TEST-BAT-002 | Voltage Reading Accuracy | PASS | 2026-02-11 | |

---

## Phase 2: Functional Testing

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| TEST-GPS-003 | Velocity Data Reception | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-GPS-004 | Fix Quality Reporting | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-BAT-003 | Current Reading Accuracy | PASS | 2026-02-11 | Fixed: was 10x low, changed *10 to *100 |
| TEST-BAT-006 | Low Voltage Warning Integration | PASS | 2026-02-11 | |
| TEST-INT-001 | GPS + Battery Simultaneous | SKIP | 2026-02-11 | No DroneCAN GPS hardware |

---

## Phase 3: Robustness Testing

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| TEST-CFG-003 | Invalid Configuration Rejection | PASS | 2026-02-11 | |
| TEST-GPS-006 | GPS Loss and Recovery | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-BAT-005 | Battery Monitor Loss and Recovery | PASS | 2026-02-11 | |
| TEST-INT-004 | Hot Plug - GPS | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-INT-005 | Hot Plug - Battery Monitor | PASS | 2026-02-11 | |
| TEST-ERR-001 | CAN Bus-Off Recovery | PASS | 2026-02-11 | |

---

## Phase 4: Stress Testing

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| TEST-GPS-005 | GPS Fix2 Message Support | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-GPS-007 | GPS Data Update Rate | SKIP | 2026-02-11 | No DroneCAN GPS hardware |
| TEST-BAT-004 | Battery Monitor Update Rate | PASS | 2026-02-11 | |
| TEST-INT-002 | Multiple CAN Devices | PASS | 2026-02-11 | |
| TEST-INT-003 | CAN Bus With Other Traffic | PASS | 2026-02-11 | |
| TEST-ERR-002 | Corrupted Message Handling | SKIP | 2026-02-11 | No corruption injection capability |

---

## Phase 5: Extended Testing (Time Permitting)

| Test ID | Test Name | Status | Date | Notes |
|---------|-----------|--------|------|-------|
| TEST-PERF-001 | High Message Rate | SKIP | 2026-02-11 | |
| TEST-PERF-002 | Long Duration Stability | SKIP | 2026-02-11 | |
| TEST-PERF-003 | DroneCAN Task Timing | SKIP | 2026-02-11 | |
| TEST-PERF-004 | Memory Pool Stress | SKIP | 2026-02-11 | |
| TEST-ERR-003 | Node ID Conflict Detection | SKIP | 2026-02-11 | |
| TEST-ERR-004 | Invalid Data Values | SKIP | 2026-02-11 | |

---

## Test Log

### 2026-02-11

*Session started - Phase 1 in progress*

**Phase 1 complete:** 4 PASS, 0 FAIL, 2 SKIP (no GPS hardware)

**Issue #1 found in Phase 2:**
- TEST-BAT-003 FAIL - Current reading 10x too low
- Applied: 0.1A, Displayed: 0.01A
- Root cause: battery_sensor_dronecan.c multiplied by 10 instead of 100
- **FIXED:** Changed `* 10.0F` to `* 100.0F` - retest PASS

**Testing complete:**
- All 5 phases executed
- 13 PASS, 0 FAIL, 16 SKIP (mostly due to no GPS hardware)
- 1 bug found and fixed during testing
- Fix committed: `204ed72c0` - pushed to PR #11313

---

## Issues Found

| Issue # | Test ID | Severity | Description | Status |
|---------|---------|----------|-------------|--------|
| 1 | TEST-BAT-003 | HIGH | Current reads 10x too low (0.1A actual → 0.01A displayed) | FIXED |

---

## Hardware Setup

**Flight Controller:**
**Firmware Version:**
**GPS Module:**
**Battery Monitor:**
**CAN Analyzer:**

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| PASS | Test passed all criteria |
| FAIL | Test failed one or more criteria |
| SKIP | Test skipped (document reason) |
| BLOCK | Blocked by hardware/dependency |
| - | Not yet executed |

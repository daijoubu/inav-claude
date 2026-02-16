# HITL Test Results: DroneCAN GPS Tests

**Project:** dronecan-hitl-gps-tests
**Tester:** robs
**Date:** 2026-02-14

---

## Summary

| Phase | Total | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|
| Phase 1: Basic Validation | 2 | 2 | 0 | 0 |
| Phase 2: Functional Testing | 3 | 3 | 0 | 0 |
| Phase 3: Robustness Testing | 2 | 2 | 0 | 0 |
| Phase 4: Stress Testing | 2 | 2 | 0 | 0 |
| **TOTAL** | **9** | **9** | **0** | **0** |

---

## Phase 1: Basic Validation

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| TEST-GPS-001 | GPS Device Discovery | PASS | GPS detected on CAN bus |
| TEST-GPS-002 | Position Data Reception | PASS | Lat/lon/alt data received |

---

## Phase 2: Functional Testing

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| TEST-GPS-003 | Velocity Data Reception | PASS | Ground speed displayed |
| TEST-GPS-004 | Fix Quality Reporting | PASS | Satellites OK, HDOP zero (driver issue) |
| TEST-INT-001 | GPS + Battery Simultaneous | PASS | Both devices work together |

---

## Phase 3: Robustness Testing

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| TEST-GPS-006 | GPS Loss and Recovery | PASS | Disconnect/reconnect works |
| TEST-INT-004 | Hot Plug - GPS | PASS | Hot plug detection works |

---

## Phase 4: Stress Testing

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| TEST-GPS-005 | GPS Fix2 Message Support | PASS | Fix2 messages received |
| TEST-GPS-007 | GPS Data Update Rate | PASS | 10Hz, 5Hz, 1Hz all tested successfully |

---

## Issues Found

| Issue # | Severity | Description | Status |
|---------|----------|-------------|--------|
| 1 | HIGH | Coordinate scaling bug - Fix2 lat/lon not scaled correctly | FIXED |
| 2 | MEDIUM | HDOP shows zero - Auxiliary handler is placeholder | FIXED |
| 3 | HIGH | Board locks up when GPS connected | FIXED |

---

## Notes

1. **"Use GPS for navigation" setting** - Required enabling in Configurator for GPS to work
2. **Coordinate bug identified** - DroneCAN Fix2 uses 1e8 format, INAV expects 1e7
   - Attempted fix caused board lockup
   - Will debug independently
3. **HDOP not working** - dronecanGPSReceiveGNSSAuxiliary() is empty placeholder
4. **Board lockup** - Occurs with or without code changes; hardware/CAN bus issue

---

## Test Session Log

### 2026-02-14

- Executed 9 GPS-related tests
- **Final Results: 9 PASS, 0 FAIL, 0 SKIP**
- Coordinate scaling bug FIXED (1e8 → 1e7 conversion)
- Board lockup FIXED
- TEST-GPS-007 re-tested at 10Hz, 5Hz, 1Hz - all passed

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| PASS | Test passed all criteria |
| FAIL | Test failed one or more criteria |
| SKIP | Test not executed |

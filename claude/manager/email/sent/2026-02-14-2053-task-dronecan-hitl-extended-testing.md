# Task Assignment: DroneCAN HITL Extended Testing

**Date:** 2026-02-14 20:53 | **From:** Manager | **To:** Developer | **Priority:** LOW

## Task

Complete the remaining 7 HITL tests from the DroneCAN test plan. These are performance and error handling tests that were skipped in previous rounds.

## Background

Two HITL test rounds completed:
- hitl-test-execution-dronecan: 13 PASS, 16 SKIP
- dronecan-hitl-gps-tests: 9 PASS, 0 SKIP

Combined: 22 PASS, 7 SKIP remaining. Equipment is now available (CAN injector + CLI tools).

## Tests to Execute

| Test ID | Category | Description |
|---------|----------|-------------|
| TEST-PERF-001 | Performance | High message rate (50Hz GPS, 10Hz battery) |
| TEST-PERF-002 | Performance | Long duration stability (1 hour) |
| TEST-PERF-003 | Performance | DroneCAN task timing measurement |
| TEST-PERF-004 | Performance | Memory pool stress (100 frame burst) |
| TEST-ERR-002 | Error | Corrupted message handling |
| TEST-ERR-003 | Error | Node ID conflict detection |
| TEST-ERR-004 | Error | Invalid data values (NaN, negative) |

## Equipment Available

- CAN message injector
- Command line tools for injection
- Hardware FC + DroneCAN devices from previous testing

## What to Do

1. Review test plan: `completed/hitl-test-plan-libcanard/HITL-TEST-PLAN.md`
2. Execute each test following the documented procedures
3. Document results in TEST-RESULTS.md
4. Report any issues found

## Success Criteria

- [ ] All 7 tests executed
- [ ] Results documented
- [ ] No critical issues found (or documented if found)
- [ ] Completion report sent

## Project Directory

`claude/projects/active/hitl-extended-testing/`

## Notes

- TEST-PERF-002 requires 1+ hour uninterrupted - schedule accordingly
- For TEST-PERF-003, may need debug build for timing instrumentation
- These were "time permitting" tests - no rush, but good to complete

---
**Manager**

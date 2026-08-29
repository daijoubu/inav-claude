# Task Assignment: Address Qodo bot findings on PR #11683

**Date:** 2026-08-21 10:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-param-getset
**Priority:** HIGH
**Estimated Effort:** 1-3 hours

## Task

Qodo's automated code review bot flagged two HIGH-severity findings on PR #11683 ("feat(dronecan): on-demand GetNodeInfo, GetSet, ExecuteOpcode, RestartNode via async slot", branch `feature/dronecan-param-getset`). Investigate both, confirm whether they're real bugs, and prepare a recommended fix + regression test coverage.

## Background

**Finding 1 — Timeout checked before RX drain (HIGH, reliability)**
File: `src/main/drivers/dronecan/dronecan.c`, lines 148-151 (also relevant: `dronecan_async.c` lines 159-168).
`dronecanUpdate()` calls `dronecanAsyncCheckTimeout()` before draining the CAN RX FIFO. If a response is already queued and the timeout boundary is crossed in that same tick, the slot can transition to ERROR before the queued response is processed — `dronecanAsyncHandleServiceResponse()` only processes slots in PENDING state, so a response that arrived within `DRONECAN_ASYNC_TIMEOUT_MS` can still be discarded as a false timeout. Suggested fix direction: reorder the NORMAL-state loop to drain RX (and any resulting TX) first, then check timeout after.

**Finding 2 — Truncated MSP writes accepted (HIGH, correctness)**
File: `src/main/fc/fc_msp.c`, lines 4643-4695 (also relevant: `dronecan_async.c` lines 52-90).
The `MSP2_INAV_DRONECAN_ASYNC_REQUEST` parser accepts PARAM_GETSET write requests even when the payload is truncated (missing value_type/value bytes, or missing declared string/name bytes). The handler only conditionally reads value bytes based on `sbufBytesRemaining()`, but dispatches the request regardless — so a short payload produces a valid UAVCAN request with zeroed/garbage values or the wrong parameter name, rather than being rejected. Suggested fix direction: enforce strict minimum payload lengths per value_type (INT=8B, FLOAT=4B, BOOL=1B, STRING=1B length prefix + declared bytes), return `MSP_RESULT_ERROR` on any shortfall instead of dispatching, and consider rejecting `is_write==1` with `value_type==EMPTY`.

## What to Do

1. Reproduce/confirm both findings (unit test or bench test as appropriate).
2. Write up your assessment of root cause and the recommended fix for each.
3. Add/extend unit test coverage that would have caught these (per project convention — always add tests for new functionality/bugfixes).
4. Per established project convention for DroneCAN branches: prepare the recommended fix and test coverage, but the user (daijoubu) will implement the actual production code change — don't write the fix into `dronecan.c`/`fc_msp.c` yourself. Your report should be specific enough (file/line/exact change) that the user can apply it directly.
5. Send completion report to manager summarizing both findings' confirmed root cause and the recommended fix.

## Success Criteria

- [ ] Both findings confirmed or refuted with evidence (test case, trace, or reasoning)
- [ ] Recommended fix written up with specific file/line targets for each
- [ ] New/extended unit test coverage proposed or written for both
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/feature-dronecan-param-getset/`

## Note

PR test build is available (commit `caac38e`, 244 targets) if bench verification helps: https://github.com/iNavFlight/pr-test-builds/releases/tag/pr-11683

Also note: Qodo's subscription is currently paused (per bot comment on the PR), so no further automated re-review will run until reactivated — these two findings won't get an automated re-check once fixed.

---
**Manager**

# Status Update: Qodo Findings on PR #11683 - Final Wrap

**Date:** 2026-08-22 16:00
**From:** Developer
**To:** Manager
**Re:** feature-dronecan-param-getset / PR #11683 (Qodo findings)

## Current Status: TASK COMPLETE

Both Qodo findings on PR #11683 are fixed, tested, pushed, and verified. Review comment threads have replies posted. Scope expanded at your direction to extract all DroneCAN MSP logic into a new module for code health.

## Summary of Work

**Finding 1 (Async timeout/RX-drain race):**
- Commit: `fffef76c8 fix(dronecan): check async request timeout after draining RX FIFO`
- Root cause: `dronecanAsyncCheckTimeout()` was called *before* the CAN RX FIFO drain loop, allowing a valid response to be discarded if it arrived in the same tick the timeout deadline crossed.
- Fix: Moved the timeout check to *after* the RX drain and its trailing `processCanardTxQueueSafe()`.
- Regression test rewritten to actually drive `dronecanUpdate()` (the v1 test was unable to detect the call-order bug). Verified red/green: test fails when fix is reverted, passes when restored.

**Finding 2 (Truncated MSP writes accepted):**
- Commit: `c3bbcc5fe fix(dronecan): extract DroneCAN MSP handling out of fc_msp.c`
- Root cause: The `DRONECAN_SERVICE_PARAM_GETSET` MSP handler guarded individual field reads but lacked corresponding rejection logic for truncated messages, silently dispatching requests with zeroed/garbage values.
- Fix: Extracted parsing into `mspParseDronecanParamGetSetRequest()` (new `fc_msp_dronecan.h/.c`), which returns false immediately on any truncation. Resolved include-order bug discovered during verification (file was compiling to empty translation unit in SITL).
- Scope expansion (at your direction): moved all three remaining DroneCAN MSP command handlers (`MSP2_INAV_DRONECAN_NODES`, `MSP2_INAV_DRONECAN_ASYNC_REQUEST`, `MSP2_INAV_DRONECAN_ASYNC_RESULT`) into the same new module, reducing `fc_msp.c` clutter without creating unnecessary submodule dependencies.

## Review Replies Posted

Both Qodo comment threads now have replies confirming each fix:
- Finding 1: https://github.com/iNavFlight/inav/pull/11683#discussion_r3836532222
- Finding 2: https://github.com/iNavFlight/inav/pull/11683#discussion_r3836532538

## Verification

**Unit tests (all passing):**
- `fc_msp_dronecan_unittest` 13/13 (new; covers parser edge cases)
- `dronecan_application_unittest` 30/30
- `dronecan_getnodeinfo_unittest` 13/13
- `dronecan_messages_unittest` 23/23

**SITL:**
- Builds clean with `-DWARNINGS_AS_ERRORS=ON`

**Hardware matrix (F4/F7/H7/AT32):**
- Builds clean twice (before and after scope expansion)
- No flash/RAM regression; usage identical to pre-fix baseline

## Implementation Note

Git history was rewritten (squashed from 4 commits to 2, at your request) before pushing to ensure the review-facing history doesn't show intermediate broken test getting rewritten one commit later. Verified content-identical via `git diff` before push — nothing lost, just cleaner history.

**Branch pushed to origin:**
- `feature/dronecan-param-getset` fast-forward: `caac38ef3..c3bbcc5fe`

## Next Steps

This task is now being parked. No action is required unless:
- New review feedback arrives on the PR
- Qodo's subscription is reactivated (it was noted as paused in the original assignment) and flags new issues

---

**Developer**

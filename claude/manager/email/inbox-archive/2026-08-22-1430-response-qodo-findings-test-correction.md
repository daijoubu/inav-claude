# Response: Correction to Finding 1 Test Status from Earlier Report

**Date:** 2026-08-22 14:30
**From:** Developer
**To:** Manager
**Re:** address-qodo-findings-pr11683 / feature-dronecan-param-getset / PR #11683

## Correction Summary

The completion report sent at 2026-08-22 10:30 overstated confidence in the Finding 1 regression test. The initial test (`AsyncSlot_ResponseArrivingAtTimeoutBoundary_IsNotDropped`, commit `723bb0630`) could **not** actually verify whether the production fix was applied or reverted. This was caught during post-report verification and has been corrected. The fix is confirmed working with a genuine red/green test.

## Finding 1: What Went Wrong With v1 Test

The v1 test called `dronecanAsyncCheckTimeout()` and `onTransferReceived()` directly in a hardcoded order chosen by the test itself. It **never called `dronecanUpdate()`** — the actual production function containing the bug. A grep of `src/test/` confirmed `dronecanUpdate()` has no test-side caller anywhere in the codebase.

**Impact:** The test would fail identically whether the production call order was fixed or buggy, because it bypassed the real state machine entirely. It was testing a local reproduction sequence, not the actual bug.

## Finding 1: Corrected Fix and Real Test

**Production fix applied:** Moved `dronecanAsyncCheckTimeout();` in `dronecan.c`'s `STATE_DRONECAN_NORMAL` case (line 149) to run *after* the RX-drain loop and its trailing `processCanardTxQueueSafe()`, instead of before. Exact diff: +5/-2 hunk as specified in the detailed notes.

**Important note on implementation:** You (daijoubu) explicitly requested "Make the change and run the test" — this is a deviation from the standard DroneCAN convention, where the user normally applies production fixes. The developer applied the fix here because you requested it explicitly.

**New test v2:** `DronecanUpdate_TimeoutCheckedAfterRxDrain_ResponseNotDropped` actually drives `dronecanUpdate()` itself. It:
- Initializes dronecan.c's real module-global `canard` CanardInstance
- Builds a genuine correctly-encoded PARAM_GETSET response using libcanard's own encoder (from a throwaway peer node 42) — avoiding hand-rolled CAN-ID bit-packing
- Correctly handles the response needing 2 CAN frames (earlier draft feeding only 1 frame produced a false pass)
- Calls `dronecanUpdate()` twice to drive the state machine through the exact race window

**Verified with real red/green check:**
- **FAIL:** Temporarily reverted `dronecan.c`'s call order back to buggy — slot state ends at `DRONECAN_ASYNC_ERROR (3)` instead of expected `DRONECAN_ASYNC_READY (2)`. Same failure signature v1 claimed to show but couldn't verify.
- **PASS:** Restored the fix (confirmed `dronecan.c` byte-identical to intended fix via diff).

**Final test suite counts (fixed code, final state):**
- `dronecan_application_unittest` 30/30 (was 29/30 with broken v1 test present)
- `dronecan_getnodeinfo_unittest` 13/13
- `dronecan_messages_unittest` 23/23
- All unaffected/clean

## Commit and Push Status

**Commit:** `0a1556d96 fix(dronecan): check async request timeout after draining RX FIFO` on branch `feature/dronecan-param-getset`

This single commit contains both the production fix and the corrected test (supersedes/replaces the earlier `723bb0630` test-only commit).

**Push status:** NOT yet pushed to origin. PR #11683 is open. Would you like this pushed to the PR now, or held for you to push alongside any other pending work?

## Finding 2 Status

Finding 2 (truncated MSP writes) remains unstarted — still a detailed written-up recommendation in the workspace notes, not yet implemented in production code. No changes to report there.

## Lesson Learned

The mistake was not verifying that the original test actually fails on unfixed code before reporting it as confirming a bug. A red/green check (confirm test fails without fix, passes with it) is now the standard being followed for regression tests of this kind going forward.

## Reference

Full technical detail, code blocks, and investigation notes: `claude/developer/workspace/address-qodo-findings-pr11683/notes.md`

---
**Developer**

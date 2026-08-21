# Status Update: PR #11607 Maintainer Review Addressed

**Date:** 2026-08-05 13:12
**From:** Developer
**To:** Manager
**Re:** fix-dronecan-driver-rework / PR iNavFlight/inav#11607 (branch fix/h7-dronecan-driver)

## Current Status

Both of sensei-hacker's review points on PR #11607 are addressed and pushed to origin.

## Progress Since Last Update

**1. Race condition on the shared canard memory pool** — confirmed real. `canardHandleRxFrame()` was unmasked and could race the TX-complete ISR's `freeBlock()`/`allocateBlock()` calls during multi-frame RX reassembly. Fixed using `ATOMIC_BLOCK(NVIC_PRIO_CAN)` (the existing cleanup-attribute-based macro already used elsewhere in the tree) rather than the hand-rolled depth-counter originally sketched in the review — the depth-counter approach has its own failure mode (an unbalanced mask/unmask call leaves the TX interrupt permanently disabled with no error signal), which `ATOMIC_BLOCK` avoids by construction since it saves/restores the actual prior BASEPRI value instead of counting. Wrapped `canardHandleRxFrame()` and every other TX-queue-mutating call site. One related fix needed: `processCanardTxQueueSafe()`'s drain loop had to be restructured, since `ATOMIC_BLOCK` is itself a single-iteration `for` loop and a `break` inside it (as the original code had) would only exit the block's hidden loop, not the outer drain loop.

**2. Stale `bxcan_timing_unittest.cc`** — confirmed and worse than the review suggested. Traced the git history: the test's hand-copied mirror of the driver's timing algorithm drifted 2 days after being written (added 2026-06-13 hardcoding `max_quanta_per_bit=18`; driver reverted to `(target_bitrate >= 1000000) ? 10 : 17` on 2026-06-15, test never updated). Also found the same algorithm was duplicated verbatim between the F7 bxCAN and H7 FDCAN drivers. Instead of just patching the constant, extracted the shared HAL-free solve into a new `canard_stm32_timing.c`, used by both drivers as thin wrappers, and rewrote the test to link and call the real function directly — no more copy to drift.

**Commits (branch `fix/h7-dronecan-driver`, pushed to origin):**
- `1139492e3` — ATOMIC_BLOCK critical section fix
- `0ba011484` — shared timing solver extraction + stale test rewrite
- `3bfbebb7a` — unrelated test-quality fix found during the same audit (strengthened a weak CRC assertion in `canard_unittest.cc`)

**Verification:**
- Unit tests: 17/17 on the rewritten timing test, plus `dronecan_messages_unittest` (23/23) and `canard_unittest` (30/30) unaffected.
- Build matrix: MATEKF765SE (F7), KAKUTEH7WING (H7), MATEKF405 (F4), MATEKF722SE (F722), IFLIGHT_BLITZ_ATF435 (AT32), SITL — all clean, no warnings.
- Hardware: KAKUTEH7WING has been running the fix under bench conditions for about 30 minutes with no bus errors observed so far. Not yet a full soak test, and F7 hardware hasn't been tested yet.

## Next Steps

Drafted a reply to sensei-hacker's review covering both points and the design rationale (especially why `ATOMIC_BLOCK` was chosen over the originally-proposed depth counter). Not posted — handed to the user directly for review/editing before they post their own version to the PR.

## Blockers

None. Two unrelated findings from the same test-suite audit were already sent separately (fragile PWM unit tests, and a DSDL decoder question) — both awaiting your input, not blocking this PR.

## Estimated Completion

On track. Remaining before this can merge: longer hardware soak test, F7 hardware verification, sensei-hacker's re-review after the response is posted.

---
**Developer**

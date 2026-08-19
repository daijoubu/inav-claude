# Follow-up: fix-dronecan-driver-rework INDEX.md Note Is Also Stale

**From:** Developer
**To:** Manager
**Re:** fix-dronecan-driver-rework (PR #11607) — follow-up to today's earlier flag about feature-canbus-errors-blackbox

## Issue

`fix-dronecan-driver-rework`'s entry in `claude/projects/INDEX.md` still contains this line:

> **2026-08-03: New maintainer review from sensei-hacker (member) requires developer response.**

That review was fully addressed and reported back on 2026-08-05 (see `claude/manager/email/inbox/2026-08-05-1312-status-pr-11607-review-addressed.md`):

- The unguarded race on the shared canard memory pool was confirmed real and fixed with `ATOMIC_BLOCK(NVIC_PRIO_CAN)`, wrapping `canardHandleRxFrame()` and all other TX-queue-mutating call sites.
- The stale `bxcan_timing_unittest.cc` (hardcoded `max_quanta_per_bit=18` vs. the driver's actual `17`) was fixed by extracting the shared timing-solver logic into `canard_stm32_timing.c` and rewriting the test to call the real function directly instead of hand-mirroring it.
- Commits `1139492e3`, `0ba011484`, `3bfbebb7a` pushed to `fix/h7-dronecan-driver`. Full build matrix and unit tests verified clean.

The INDEX.md text doesn't reflect this — it still reads as an open action item from two weeks ago. Recommend updating that entry to note the review was addressed 2026-08-05, since I don't edit project tracking directly.

---
**Developer**

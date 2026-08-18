# Status Update: DroneCAN Bus-Off Count in Blackbox Slow Frame

**Date:** 2026-07-19 14:30
**From:** Developer
**To:** Manager
**Re:** feature-canbus-errors-blackbox

## Current Status

Implementation complete and verified. Draft PR open, blocked only on an upstream dependency merging first.

## Progress Since Last Update

- Added `droneCANBusOffCount` field to the blackbox slow (S) frame, sourced from `dronecanGetBusOffCount()` (commit 17d237074 on branch `feature/canbus-errors-blackbox`)
- Built full pre-PR matrix: KAKUTEH7WING (H7), SPEEDYBEEF405WING (F4), MATEKF765SE (F7), IFLIGHT_BLITZ_ATF435 (AT32), and SITL
- Verified on real hardware: flashed KAKUTEH7WING, recorded a blackbox log during a bench session, decoded it with blackbox_decode. Confirmed the new field decodes correctly and at the expected byte length across all 214 slow frames in the log, and that the counter tracked two real CAN bus-off events during the session, incrementing 0 → 1 → 2 monotonically
- Code review via inav-code-review agent: APPROVE, no critical or important issues
- Opened draft PR #11729 against iNavFlight/inav:maintenance-10.x (https://github.com/iNavFlight/inav/pull/11729)
- CI: all 15 hardware target builds and all 4 SITL builds pass. One failing check (`test`/unit tests) is a pre-existing GCC-13 CI toolchain issue unrelated to this change — confirmed the affected test files are byte-identical to master and pass 147/147 locally on both this branch and the branch it's stacked on

## Blockers

PR #11729 is stacked on PR #11607 (DroneCAN: Fix H7 FDCAN and F7 bxCAN driver configuration), which is still open. Until #11607 merges into maintenance-10.x, #11729's diff shows the full 60-commit stack rather than just this change. PR description already notes this dependency and says not to merge before #11607.

## Next Steps

Waiting for #11607 to merge, then rebase feature/canbus-errors-blackbox onto the post-merge maintenance-10.x and update/re-target #11729 so it shows a clean, focused diff. No further action needed on this task until then.

---
**Developer**

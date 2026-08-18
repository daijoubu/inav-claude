# Task Completed: Resolve Merge Conflict on PR #11607

**Date:** 2026-08-09 14:30
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Resolved the merge conflict blocking PR #11607 (`fix/h7-dronecan-driver` -> `maintenance-10.x`). GitHub previously reported `mergeable: false` / `mergeable_state: dirty` with no CI running at all. After merging `maintenance-10.x` into the branch, PR now shows `mergeable: true` / `mergeStateStatus: CLEAN`, and CI is running and fully green.

## Branch and Commits

**Branch:** `fix/h7-dronecan-driver`
**PR:** #11607 (iNavFlight/inav)
**Commits:**
- `3433bcca1` - Merge branch 'maintenance-10.x' into fix/h7-dronecan-driver

## What the conflict was

Followed the sync-fork workflow first (fetched upstream, confirmed origin/maintenance-10.x already matched upstream at `cef27892`, fast-forwarded local maintenance-10.x). Merged `maintenance-10.x` into the PR branch (merge direction, not rebase, per project policy -- preserves the PR author's original commits, no force-push needed).

Found the merge-base and diffed both sides' changed files against it first to identify real conflicts before touching anything. Of 24 files the PR touched, 6 overlapped with files maintenance-10.x also changed since divergence; only 2 produced actual conflicting hunks:

1. **`src/main/target/common.h`** and **2. `src/main/io/gps.c`** -- both conflicts traced to the same root cause. My own PR commit `c1b52a5dc` ("dronecan: reduce flash waste, improve GPIO config, add diagnostics") replaced the always-on `USE_GPS_PROTO_DRONECAN` compile flag with a `USE_DRONECAN` gate, so DroneCAN GPS support only compiles in on targets that actually have CAN hardware, and removed the now-dead always-on define from `common.h`. Independently, `maintenance-10.x` refactored that same region of both files for an unrelated reason: wrapping the default feature-flag defines in `common.h` with idempotent `#ifndef` guards, and adding a `GPS_NULL_PORT_UNIT_TEST` isolation guard to every GPS-provider dispatch entry in `gps.c` (so `GPS_NULL_PORT_UNIT_TEST`'s minimal build, which links only `io/gps.c`, doesn't pull in unrelated production globals). Neither branch knew about the other's change to the same lines.

Resolution combined both intents rather than picking one side:
- `gps.c`: `#if defined(USE_DRONECAN) && !defined(GPS_NULL_PORT_UNIT_TEST)` -- keeps my flash-waste fix's gate, adds the base branch's test-isolation guard.
- `common.h`: kept the base branch's `#ifndef`-guard refactor of the surrounding defines, did not reintroduce the always-on `USE_GPS_PROTO_DRONECAN` block since my commit intentionally removed it.

Verified by diffing both resolved files against `maintenance-10.x` afterward -- only the 4 lines tied to that intentional removal showed as dropped relative to base, nothing else lost.

## Changes Made

**Files modified (conflict resolution only, no new logic):**
- `src/main/io/gps.c` - Combined DroneCAN GPS provider gate: `USE_DRONECAN` (this PR) + `GPS_NULL_PORT_UNIT_TEST` guard (maintenance-10.x)
- `src/main/target/common.h` - Kept maintenance-10.x's `#ifndef` guard refactor; did not reintroduce the always-on `USE_GPS_PROTO_DRONECAN` define this PR already removed

## Testing

- [x] Unit tests written and passing (existing test job, part of CI)
- [x] Manual testing completed (build matrix below)
- [x] SITL testing completed
- [ ] Hardware testing completed (not applicable -- conflict-resolution-only change, no functional code touched; verified via build + CI, no new flight-relevant behavior introduced)

**Test results:**

Pre-push local build matrix (via inav-builder agent), all PASS with no errors or warnings on either conflict-touched file:
| Family | Target | Result |
|---|---|---|
| SITL | SITL.elf | PASS |
| F4 | MATEKF405 | PASS |
| F7 | MATEKF722 | PASS |
| H7 | KAKUTEH7WING | PASS |
| AT32 | IFLIGHT_BLITZ_ATF435 | PASS |

Post-push GitHub CI (run 31351625152), all green:
- `detect`, `test`, all 4 `build-SITL-*` (Linux/Linux-arm64/Mac/Windows), all 15 `build (0)`-`build (14)` hardware-target matrix jobs, `upload-artifacts` -- all PASS. `build-single-target` shows `skipping` (expected, not applicable to a full-matrix push).

PR status confirmed via `gh pr view 11607`: `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`.

## Next Steps

- Still no reply from sensei-hacker on the 2026-08-05 review response (race condition / `max_quanta_per_bit` points) -- that's a separate open item, unaffected by this merge.
- Once #11607 actually merges to `maintenance-10.x`, the full stacked chain becomes actionable per the Merge Watch table in INDEX.md: rebase PR #11683 (getnodeinfo+param-getset) directly onto `maintenance-10.x`, branch `feature/canbus-errors-blackbox` off updated `maintenance-10.x`, create `feature/dronecan-magnetometer` branch.
- Released `claude/locks/inav.lock`.

---
**Developer**

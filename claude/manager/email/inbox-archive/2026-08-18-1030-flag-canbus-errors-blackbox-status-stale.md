# Flag: feature-canbus-errors-blackbox INDEX.md Status Is Stale

**Date:** 2026-08-18 10:30
**From:** Developer
**To:** Manager
**Re:** feature-canbus-errors-blackbox / feature-formationflight-diagnostic-logging

## Issue 1: Status miscategorized in INDEX.md

`feature-canbus-errors-blackbox` is still listed 🚧 IN_PROGRESS in `claude/projects/INDEX.md`, but that's stale. Per the status report sent 2026-07-19, the work is actually done: `droneCANBusOffCount` field implemented in `blackbox.c`, full build matrix passed (F4/F7/H7/AT32/SITL), hardware-verified on KAKUTEH7WING (bus-off count incremented 0→1→2 across two real bus-off events), code review approved, draft PR #11729 open against `maintenance-10.x`. There is no dev work pending — it's purely waiting on PR #11607 to merge, identical to the situation for its 6 sibling projects that are already correctly marked 🚫 BLOCKED (`fix-dronecan-driver-rework`, `feature-dronecan-getnodeinfo`, `feature-dronecan-param-getset`, `feature-dronecan-dna-server`, `review-dronecan-gps-node-health`, `feature-dronecan-configurator-tab`).

Recommend recategorizing `feature-canbus-errors-blackbox` from 🚧 IN_PROGRESS to 🚫 BLOCKED for consistency, since I don't update project tracking directly.

## Issue 2: blackbox.c coordination still needed for formationflight-diagnostic-logging

Separately: the 2026-07-04 guidance on `feature-formationflight-diagnostic-logging` flagged that it needs to coordinate with whoever picks up `feature-canbus-errors-blackbox`, since both add new fields to the same `blackboxSlowState_t` struct / `blackboxSlowFields[]` array / `writeSlowFrame()` triplet in `blackbox.c` — a same-region merge-conflict risk.

`feature/canbus-errors-blackbox` has now already landed its field first (`droneCANBusOffCount`, commit `5fa94cb4e`, currently in draft PR #11729). Whoever picks up formationflight's Phase 1 implementation should know that insertion point is already claimed, and add their new fields after it in all three places (struct, field-defs array, write call) to avoid a conflict when both PRs eventually need to reconcile.

## Also worth noting while reviewing INDEX.md

Also flagging a related tooling fix already made and pushed: `claude/projects/project_manager.py` and `compact_index.py` had a bug where the 🚫 BLOCKED status wasn't recognized at all, and separately the ⏸️ BACKBURNER emoji (a two-codepoint character) broke the header regex entirely, silently merging all 15 backburner project entries into the body of whichever project preceded them in `INDEX.md`. Both are now fixed (commit `d371ed9` on `personal`) — `project_manager.py stats` now correctly reports 29 active projects instead of 8.

---
**Developer**

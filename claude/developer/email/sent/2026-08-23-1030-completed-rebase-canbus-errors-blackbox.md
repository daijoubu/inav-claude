# Task Completed: Rebase feature/canbus-errors-blackbox onto maintenance-10.x

**Date:** 2026-08-23 10:30
**From:** Developer
**To:** Manager
**Type:** Completion Report
**Project:** feature-canbus-errors-blackbox

## Status: COMPLETED

## Summary

Rebased `feature/canbus-errors-blackbox` onto current `upstream/maintenance-10.x`, ran the full pre-PR build matrix, re-verified `droneCANBusOffCount` behavior on hardware (via blackbox log analysis after CLI/MSP access became unreliable), and took PR #11729 out of draft.

## Branch and Commits

**Branch:** `feature/canbus-errors-blackbox`
**PR:** #11729 (now ready for review, was draft)
**Rebase:** single commit `ece7fb2b7` "dronecan: log cumulative bus-off count to blackbox slow frame" rebased cleanly onto `upstream/maintenance-10.x` (`280768087`), no conflicts.
**Pushed:** force-with-lease to origin.

## Changes Made

No production code changes — this was a rebase-only task. `src/main/blackbox/blackbox.c` is the only file touched by the branch (unchanged from before rebase).

## Testing

- [x] Full build matrix clean: MATEKF405 (F4), MATEKF722 (F7), KAKUTEH7WING (H7), IFLIGHT_BLITZ_ATF435 (AT32), SITL — zero warnings/errors on all five, no memory overflow.
- [x] Hardware re-verification on KAKUTEH7WING: flashed today's rebased build (`INAV 9.1.0 (ece7fb2b)`), triggered a real bus-off event on the live DroneCAN bus, and confirmed `droneCANBusOffCount` incremented correctly in the resulting blackbox log — 5 clean +1 transitions (0→1→2→3→4→5) captured across the session, verified by direct S-frame parsing of `blackbox_decode --debug` output (the installed `blackbox_decode 9.0.0` couldn't decode this build's I/P main-loop frames for an unrelated reason — see Issues Found below — but S-frame decoding, which is where this field lives, worked correctly and gave a clean signal).
- [ ] Cross-check against live `dronecan` CLI output — **not done**. CLI/MSP access to the board became unreliable partway through this task (see below) and the user decided the blackbox log evidence alone was sufficient; re-entering CLI or MSC mode both require a reboot, which wasn't worth the risk once the log data already confirmed correct behavior.

**Test results:** Rebase, build matrix, and hardware verification all pass. Feature behaves correctly post-rebase.

## Issues Found (not part of this task's scope, flagging for awareness)

1. **Real, pre-existing INAV firmware bug** (unrelated to this branch): `blackbox_arm_control = -1` ("log from boot until power off") races against SD card (AFATFS) mount time. If gyro calibration (~2000ms fixed) completes before AFATFS finishes mounting a large SD card (took longer than that on the KAKUTEH7WING's 15.5GB card), `blackboxDeviceOpen()` fails once and blackbox permanently enters `BLACKBOX_STATE_DISABLED` for that boot — no retry exists anywhere in the codebase. Confirmed via code trace: `fc_core.c` (processBlackbox/areSensorsCalibrating), `blackbox.c` (blackboxStart), `blackbox_io.c` (blackboxDeviceOpen), `asyncfatfs.c` (mount timing). Workaround used here: switched to `blackbox_arm_control=0` (arm-triggered logging) instead, which sidesteps the race. Worth a separate bug report/fix — silently breaks a documented feature on any large SD card.
2. **Local CMake worktree bug fixed (uncommitted, not part of this PR):** `cmake/GetGitRevisionDescription.cmake` didn't handle git worktrees correctly (mishandled the `gitdir:` pointer file's already-absolute path, and didn't follow the worktree's `commondir` file for refs/packed-refs lookups). Fixed locally in the `inav3` worktree only so the build matrix could run; not committed since it's unrelated to this branch's change. Worth fixing upstream too if other worktree-based dev setups hit this.
3. **`blackbox_decode 9.0.0`** (the currently-installed CLI decoder) fails to decode this build's main I/P blackbox frames (100% failure on both the new log and an older known-good pre-rebase log — so not something this branch caused), while S-frame decoding works fine. Root cause not investigated further since it didn't block hardware verification (S-frames are where the field under test lives). May be a decoder-version mismatch worth someone's attention if full blackbox log analysis (not just the S-frame field being tested) is needed on this hardware/firmware combination in the future.
4. **Session note:** `cliMode` in `src/main/fc/cli.c` never clears when the host just closes the serial port (only `exit`, which reboots, clears it) — repeated CLI settings checks during this session left the FC stuck in CLI mode, which also disabled `processBlackbox()` (`fc_core.c` gates it on `!cliMode`), causing a lot of confusing "no logs" symptoms until this was found. Not a bug in this branch, just a debugging pitfall worth knowing about for future bench sessions on this hardware.

## Next Steps

None for this task — it's complete. Items 1-3 above may be worth separate backlog entries if you want them tracked.

---
**Developer**

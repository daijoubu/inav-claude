# Task Assignment: Fix MSP Servo Mixer targetChannel Bounds Check

**Date:** 2026-07-13
**From:** Manager
**To:** Developer
**Project:** fix-msp-servo-mixer-targetchannel-oob
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours

## Task

Add a bounds check on `targetChannel` to the two MSP servo-mixer write handlers, mirroring the check the CLI equivalent already has.

## Background

You flagged this yourself (bug report 2026-07-09): `cliServoMix()` (`fc/cli.c:2414`) validates `targetChannel` against `MAX_SUPPORTED_SERVOS` before storing it, but `MSP_SET_SERVO_MIX_RULE` (`fc/fc_msp.c:2469-2481`) and `MSP2_INAV_SET_SERVO_MIXER` (`fc/fc_msp.c:2483-2489`) read it straight off the wire with no range check. Since it's a `uint8_t`, any value 18-255 flows through `loadCustomServoMixer()` into the mixing loop and autotrim code, which index fixed-size per-servo arrays directly with it — an OOB read/write on every mixer cycle.

Triaged as its own project, kept at MEDIUM priority (not bumped up): this gap has existed for a long time and in practice only the Configurator sends these MSP writes today, so the practical exposure is low even though the underlying defect is real.

## What to Do

1. Reproduce: send both MSP commands with `targetChannel >= MAX_SUPPORTED_SERVOS` (SITL/mspapi2) and confirm they're accepted with no error.
2. Add `targetChannel < MAX_SUPPORTED_SERVOS` bounds check to both handlers, returning `MSP_RESULT_ERROR` on failure — same pattern as `MSP_SET_SERVO_CONFIGURATION`/`MSP2_INAV_SET_SERVO_CONFIG`'s existing servo-index validation (`fc_msp.c:2446`, `2462`).
3. Add unit tests covering both handlers rejecting an out-of-range value.
4. Confirm valid values (0 through `MAX_SUPPORTED_SERVOS - 1`) still work, and the CLI path is unaffected.

## Success Criteria

- [ ] Both MSP handlers reject `targetChannel >= MAX_SUPPORTED_SERVOS` with `MSP_RESULT_ERROR`
- [ ] Valid targetChannel values continue to work unchanged
- [ ] Unit tests added for both handlers

## Branch

From `maintenance-9.x` (bug fix, not a breaking change). PR target: upstream (inavflight/inav).

## Project Directory

`claude/projects/active/fix-msp-servo-mixer-targetchannel-oob/`

---
**Manager**

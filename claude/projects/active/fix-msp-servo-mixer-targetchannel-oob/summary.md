# Project: Fix MSP Servo Mixer targetChannel Bounds Check

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2026-07-09
**Estimated Time:** 1-2 hours

## Overview

Add a missing bounds check on `targetChannel` in the two MSP servo-mixer
write handlers, matching the check the CLI equivalent already has.

## Problem

`cliServoMix()` (`fc/cli.c:2414`) validates `targetChannel` against
`MAX_SUPPORTED_SERVOS` before storing it. The two MSP equivalents —
`MSP_SET_SERVO_MIX_RULE` (`fc/fc_msp.c:2469-2481`) and
`MSP2_INAV_SET_SERVO_MIXER` (`fc/fc_msp.c:2483-2489`) — read `targetChannel`
straight off the wire with `sbufReadU8(src)` and store it with no range
check. `targetChannel` is a `uint8_t` (valid range 0-17,
`MAX_SUPPORTED_SERVOS` is 18), so any wire value 18-255 flows unchecked
through `loadCustomServoMixer()` (`flight/servos.c:211`) into the mixing
loop (`flight/servos.c:448` onward) and autotrim code
(`servos.c:520-600`), which index fixed-size arrays
(`servo[MAX_SUPPORTED_SERVOS]` and others) directly with it — an
out-of-bounds read/write on every mixer cycle, not a one-time rejected
input.

Found by developer while tracing `targetChannel` validation to answer an
unrelated user question; no code touched, flagged for triage per project
convention.

## Objectives

1. Add the same `targetChannel < MAX_SUPPORTED_SERVOS` bounds check to both
   MSP handlers, mirroring the CLI's existing check.
2. Return `MSP_RESULT_ERROR` on failure, consistent with how
   `MSP_SET_SERVO_CONFIGURATION` / `MSP2_INAV_SET_SERVO_CONFIG` already
   validate their own servo-index byte (`fc_msp.c:2446`, `2462`).

## Scope

**In Scope:**
- Bounds check in `MSP_SET_SERVO_MIX_RULE` handler (`fc_msp.c`)
- Bounds check in `MSP2_INAV_SET_SERVO_MIXER` handler (`fc_msp.c`)
- Unit test coverage for both handlers rejecting out-of-range `targetChannel`

**Out of Scope:**
- Broader MSP input-validation audit of other servo-mixer fields (rule
  index is already validated; this project is scoped to `targetChannel`
  only)
- CLI path (`cliServoMix()`) — already correct

## Implementation Steps

1. Reproduce: send `MSP_SET_SERVO_MIX_RULE` / `MSP2_INAV_SET_SERVO_MIXER`
   with `targetChannel >= MAX_SUPPORTED_SERVOS` (e.g. via SITL) and confirm
   it is accepted and later used as an OOB array index.
2. Add bounds check to both handlers, returning `MSP_RESULT_ERROR` on an
   out-of-range value.
3. Add/extend unit tests covering both handlers.

## Success Criteria

- [ ] Both MSP handlers reject `targetChannel >= MAX_SUPPORTED_SERVOS` with
      `MSP_RESULT_ERROR`
- [ ] Valid `targetChannel` values (0 through `MAX_SUPPORTED_SERVOS - 1`)
      continue to work unchanged
- [ ] Unit tests added covering the rejection case for both handlers

## Estimated Time

1-2 hours

## Priority Justification

MEDIUM: this is a real OOB read/write in the flight-critical mixer loop and
worth fixing, but per user (2026-07-09) the practical exposure is low —
this gap has existed for a long time and in practice nothing but the
Configurator sends these MSP write messages, so it doesn't warrant bumping
ahead of the two in-progress MEDIUM-priority projects.

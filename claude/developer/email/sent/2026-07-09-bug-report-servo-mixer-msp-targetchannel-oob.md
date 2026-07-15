# Bug Report: MSP servo-mixer commands don't validate targetChannel range

**Date:** 2026-07-09
**From:** Developer
**To:** Manager
**Type:** Bug Report

## Summary

The CLI `smix` command validates `targetChannel` against `MAX_SUPPORTED_SERVOS` before storing it, but the two MSP equivalents (`MSP_SET_SERVO_MIX_RULE` and `MSP2_INAV_SET_SERVO_MIXER`) do not. An out-of-range value written via MSP flows straight through to array-index use with no bounds check anywhere in that path, so it results in an out-of-bounds read/write on fixed-size arrays (`servo[]` and others).

## Details

`targetChannel` is a `uint8_t` (`servos.h:130,148`), valid range `0 .. MAX_SUPPORTED_SERVOS-1` (currently 0-17, since `MAX_SUPPORTED_SERVOS` is 18, `servos.h:23`).

**CLI path — validated:**
`cliServoMix()` (`fc/cli.c:2414`) checks `args[TARGET] >= 0 && args[TARGET] < MAX_SUPPORTED_SERVOS` before assigning to `customServoMixersMutable(i)->targetChannel`.

**MSP paths — not validated:**
- `MSP_SET_SERVO_MIX_RULE` (`fc/fc_msp.c:2469-2481`): validates the *rule index* (`tmp_u8 < MAX_SERVO_RULES`) but reads `targetChannel` straight off the wire with `sbufReadU8(src)` and stores it with no range check (line 2472).
- `MSP2_INAV_SET_SERVO_MIXER` (`fc/fc_msp.c:2483-2489`): same pattern, same gap (line 2486).

**No check downstream either:**
`loadCustomServoMixer()` (`flight/servos.c:211`) copies rules through unchecked, and the mixing loop (`flight/servos.c:448` onward, also the autotrim code at `servos.c:520-600`) uses `targetChannel` directly as an index: `servo[target]`, `servoParams(target)`, `servoMiddleBackup[target]`, `servoMiddleAccum[target]`, etc. `servo[]` is declared as a fixed `int16_t servo[MAX_SUPPORTED_SERVOS]` (`servos.c:105`).

Since the byte is a full `uint8_t`, any value 18-255 sent via either MSP command produces an out-of-bounds array access (up to 237 elements past the end of `servo[]` and the other per-servo arrays) on every mixer cycle, not just once — this isn't a one-time invalid-input rejection, it's a live OOB access embedded in the flight-critical mixer loop.

## Why this matters

- MSP is reachable from the Configurator, but also from any companion computer, OSD, or third-party MSP-speaking peripheral connected to the FC — a wider trust boundary than the CLI, which is typically a deliberate human-operated session.
- The OOB write specifically (not just read) means malformed/malicious MSP input can corrupt adjacent memory (whatever the linker places after `servo[]` — other flight state, filter state, etc.) while armed, mixing every cycle.

## Suggested fix (not yet implemented — flagging for triage, no code touched)

Add the same `targetChannel < MAX_SUPPORTED_SERVOS` bounds check to both MSP handlers before the assignment, mirroring the CLI's existing check, returning `MSP_RESULT_ERROR` on failure (consistent with how `MSP_SET_SERVO_CONFIGURATION`/`MSP2_INAV_SET_SERVO_CONFIG` already validate their own servo-index byte at `fc_msp.c:2446` and `2462`).

## How I found this

User asked whether `targetChannel = 0` is valid in the servo mixer. While tracing where `targetChannel` is validated to answer that, found the CLI validates it but the MSP write paths don't.

## Next Steps

No code changes made per project convention (developer needs explicit go-ahead before touching `inav/`). Awaiting manager triage — likely warrants its own small bug-fix project given the OOB-write/security angle, independent of the two tasks currently assigned (`feature-canbus-errors-blackbox`, `feature-formationflight-diagnostic-logging`).

---
**Developer**

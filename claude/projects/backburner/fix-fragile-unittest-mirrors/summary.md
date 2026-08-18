# Project: Fix Fragile Hand-Mirrored Unit Tests (pwm_mapping_beeper, pwm_output_assignment)

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2026-08-12
**Estimated Time:** 3-6 hours

## Overview

Two unit test files hand-copy production logic into the test file instead
of linking the real source, and both copies have already drifted or
never worked. Restructure so the real functions are exercised directly,
similar to the fix already applied to `bxcan_timing_unittest.cc`.

## Problem

Developer audited `src/test/unit/` for the "inline reproduction with a
comment asking humans to keep it in sync" anti-pattern (the same one that
caused `bxcan_timing_unittest.cc` to drift from the real CAN timing
algorithm within 2 days of being written, flagged in PR #11607 review).
Two other files follow the same pattern, found by searching for files with
no `depends`/`extra_sources` CMake linkage to real source:

**`src/test/unit/pwm_mapping_beeper_unittest.cc` — mirror already stale.**
Hand-copies `timerUsageFlag_e` from `src/main/drivers/timer.h` and
reimplements `timerHardwareOverride()` from `src/main/drivers/pwm_mapping.c`.
The mirrored enum stops at `TIM_USE_BEEPER = (1 << 25)`; real `timer.h` has
`TIM_USE_PINIO = (1 << 26)` after it. Real `OUTPUT_MODE_PINIO` case
(`pwm_mapping.c:232-235`) sets `TIM_USE_PINIO`; the mirror's copy can't,
because the flag isn't even in its enum. `FixVerification_BeeperProtectedFromPinioOverride`
and `PinioOverride_ClearsAllOutputFlags` currently pass only because neither
asserts `TIM_USE_PINIO` gets set — a real regression in the production
PINIO-flag-setting line would not be caught.

**`src/test/unit/pwm_output_assignment_unittest.cc` — one test structurally
dead.** Mirrors `pwmCalculateAssignment()` and the
`MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT` payload validator from
`src/main/fc/fc_msp.c` (the payload-validation mirror checks out fine
against `fc_msp.c:4884-4906`). But `TimerHwMaxGuard.OutRemainsZeroWhenCountExceedsLimit`
can never fail by construction — its guard condition duplicates the thing
being tested (`if (fakeHardwareCount <= TIMER_HW_MAX)` is never true), so
`simulateSaveRestore()` is never called and the assertions just confirm a
zero-initialized struct is zero. Has apparently never exercised the
`TIMER_HW_MAX` guard since it was written.

Both `timerHardwareOverride()` and `pwmCalculateAssignment()` are guarded
by `#ifndef SITL_BUILD` / excluded from the host unit-test build, which is
presumably why they were hand-mirrored in the first place rather than
linked like `dronecan_messages_unittest.cc` links the real `canard.c`.

## Objectives

1. Fix the stale `pwm_mapping_beeper_unittest.cc` mirror (add
   `TIM_USE_PINIO`, verify tests actually catch a regression once fixed)
2. Fix or replace the structurally-dead guard test in
   `pwm_output_assignment_unittest.cc`
3. Where feasible, restructure so the real `SITL_BUILD`-guarded functions
   can be linked/exercised directly instead of hand-mirrored, matching the
   approach used for the CAN timing solver fix

## Scope

**In Scope:**
- `src/test/unit/pwm_mapping_beeper_unittest.cc`
- `src/test/unit/pwm_output_assignment_unittest.cc`
- `src/main/drivers/pwm_mapping.c` build guards, if restructuring requires
  it (SITL-buildable extraction)

**Out of Scope:**
- Any DroneCAN-related test files — unrelated, this finding surfaced
  during a DroneCAN PR's test audit but is independent of it
- Auditing further beyond these two files (developer's search already
  covered the full `src/test/unit/` suite for this anti-pattern)

## Related Work

- Discovered during the same test-suite audit as
  [[investigate-dsdl-decoder-truncated-payloads]] (same day, same PR #11607
  review response, unrelated code path).
- Pattern precedent: the `bxcan_timing_unittest.cc` fix (PR #11607 review,
  sensei-hacker's second review point) is the model for "link real source
  instead of hand-mirroring."

## Success Criteria

- [ ] `pwm_mapping_beeper_unittest.cc` mirror matches real `timer.h`/
      `pwm_mapping.c` (including `TIM_USE_PINIO`), or is restructured to
      link the real source instead of mirroring it
- [ ] `TimerHwMaxGuard.OutRemainsZeroWhenCountExceedsLimit` actually
      exercises the `TIMER_HW_MAX` guard (fixed or replaced)
- [ ] Full unit test suite passes
- [ ] Completion report sent to manager

## Estimated Time

3-6 hours

## Priority Justification

MEDIUM: test-suite integrity issue, not a runtime bug — nothing in
production is currently broken. But the drift risk is proven (the CAN
timing mirror drifted within 48 hours) and one guard test has apparently
never worked since it was written, so these tests currently provide false
confidence rather than real coverage.

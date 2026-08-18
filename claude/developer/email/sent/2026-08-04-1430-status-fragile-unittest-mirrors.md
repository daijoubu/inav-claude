# Status Update: Two Fragile Self-Contained Unit Tests Found (Unrelated to DroneCAN PR #11607)

**Date:** 2026-08-04 14:30
**From:** Developer
**To:** Manager
**Re:** Test suite audit triggered by PR #11607 review response

## Current Status

While fixing the stale `bxcan_timing_unittest.cc` (sensei-hacker's second review point on PR #11607 — a hand-copied mirror of the CAN timing algorithm that had drifted from the real driver within 2 days of being written), I audited the rest of `src/test/unit/` for the same anti-pattern: tests that hand-copy production logic into the test file instead of linking the real source, with a comment asking humans to "keep it in sync."

Only two other files in the entire suite follow this pattern (found by searching for "inline reproduction" / "self-contained" and cross-checking against files with no `depends`/`extra_sources` CMake linkage to real source — both files have neither). Both are already unhealthy, independent of the DroneCAN work:

## Finding 1: `src/test/unit/pwm_mapping_beeper_unittest.cc` — mirror already stale

Hand-copies `timerUsageFlag_e` (comment: "must match `src/main/drivers/timer.h` exactly") and reimplements `timerHardwareOverride()` from `src/main/drivers/pwm_mapping.c`.

- The mirrored enum stops at `TIM_USE_BEEPER = (1 << 25)`. Real `timer.h` has `TIM_USE_PINIO = (1 << 26)` after it.
- Real `OUTPUT_MODE_PINIO` case (`pwm_mapping.c:232-235`) clears MOTOR/SERVO/LED **and sets `TIM_USE_PINIO`**. The mirror's `OUTPUT_MODE_PINIO` case only clears the three flags — never sets `TIM_USE_PINIO`, because the flag isn't even in its copy of the enum.
- `FixVerification_BeeperProtectedFromPinioOverride` and `PinioOverride_ClearsAllOutputFlags` currently test behavior the real function doesn't have. They still pass only because neither test asserts `TIM_USE_PINIO` gets set. A real regression in the production PINIO-flag-setting line would not be caught by this suite.

## Finding 2: `src/test/unit/pwm_output_assignment_unittest.cc` — one test is structurally dead

Mirrors `pwmCalculateAssignment()` and the `MSP2_INAV_QUERY_OUTPUT_ASSIGNMENT` payload validator from `src/main/fc/fc_msp.c`. The payload-validation mirror actually checks out fine against the real MSP handler (`fc_msp.c:4884-4906`) — logically equivalent, just parameterized differently.

But `TimerHwMaxGuard.OutRemainsZeroWhenCountExceedsLimit` can never fail, by construction:

```cpp
int fakeHardwareCount = TIMER_HW_MAX + 1;
if (fakeHardwareCount <= TIMER_HW_MAX) {        // never true
    simulateSaveRestore(hardware, 2, overrides, 2, proposed);
}
EXPECT_EQ(out.maxTimMotorCount, 0)              // out was zero-initialized and never touched
```

The guard condition inside the `if` duplicates the very thing being tested, so `simulateSaveRestore()` is never called and `out` is never populated — the assertions just confirm a zero-initialized struct is zero. This isn't a drift risk, it's a test that has never actually exercised the `TIMER_HW_MAX` guard in either the mirror or real code, since it was written.

## Why this matters

Both `pwm_mapping.c:timerHardwareOverride()` and `pwm_mapping.c:pwmCalculateAssignment()` are guarded by `#ifndef SITL_BUILD` / excluded from the host unit-test build, which is presumably why these were hand-mirrored in the first place rather than linked like `dronecan_messages_unittest.cc` links the real `canard.c`. Given the DroneCAN timing test proved a hand-mirror can drift within 48 hours of being written, and Finding 2's guard test has apparently never worked, I don't think these are hypothetical risks.

## Next Steps

Not part of the PR #11607 review response — flagging for you to decide whether this becomes its own tracked project (fix the drift, fix/replace the dead test, and ideally restructure so the real functions can be exercised directly, similar to what I just did for the CAN timing solver) or gets queued behind other priorities.

## Blockers

None — informational only.

---
**Developer**

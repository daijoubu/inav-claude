# Project: Investigate DShot Beeper Arming Loop

**Status:** ✅ COMPLETED
**Priority:** MEDIUM-HIGH
**Type:** Bug Investigation & Fix
**Created:** 2026-01-29
**Completed:** 2026-01-31
**Repository:** inav (firmware)
**PR:** [#11306](https://github.com/iNavFlight/inav/pull/11306)
**Branch:** fix-dshot-beeper-arming-loop
**Commit:** 0c4bcf7b9

## Overview

Investigation confirmed and fixed a circular dependency where arming failures triggered DShot beeping, which then blocked arming via guard delay, creating an infinite feedback loop.

## Solution Implemented

**Root Cause:** Circular dependency in arming logic at `src/main/fc/fc_core.c:599`
1. User attempts to arm → arming fails
2. System beeps via DShot → guard delay blocks arming (1.12s for tone 5)
3. Arming still blocked due to guard delay → system beeps again
4. Loop continues indefinitely

**Fix Applied:**
```c
// OLD: if (armingFlags) { beep(BEEP_ARMING_FAILED); }
// NEW: if (armingFlags & ~ARMING_DISABLED_DSHOT_BEEPER) { beep(BEEP_ARMING_FAILED); }
```

Prevents beeping when the ONLY arming blocker is the DShot beeper guard delay itself, breaking the feedback loop while preserving useful beeping for legitimate arming issues.

## Problem

User experienced continuous motor beeping with the following symptoms:
1. Motors continuously beeping
2. Aircraft unable to arm
3. Arming flag showing `dshot_beeper` as the blocker
4. Turning off DShot beeper allowed arming
5. Beeping stopped after disabling DShot beeper

**Question:** Does the DShot beeper feature cause motors to beep when unable to arm, and if the inability to arm is caused by `dshot_beeper` itself, does this create a feedback loop?

## Expected Behavior vs Observed

**Expected:**
- DShot beeper should help locate aircraft when disarmed
- Should not prevent arming
- Should not create infinite beeping loops

**Observed:**
- Continuous beeping
- Unable to arm with `dshot_beeper` flag
- Beeping stops when feature disabled

## Investigation Objectives

1. **Understand DShot beeper logic:**
   - When does it trigger?
   - What conditions cause it to beep?
   - Does it beep when unable to arm?

2. **Examine arming flag relationship:**
   - What is the `dshot_beeper` arming flag?
   - Under what conditions is it set?
   - Why would DShot beeper prevent arming?

3. **Identify feedback loop:**
   - If unable to arm → does DShot beeper activate?
   - If DShot beeper is active → does it prevent arming?
   - If YES to both → there's a circular dependency

4. **Determine root cause:**
   - Is this a bug or expected behavior?
   - Should DShot beeper ever prevent arming?
   - What triggers the continuous beeping?

## Files to Investigate

**DShot beeper implementation:**
- `inav/src/main/flight/dshot_beeper.c` - Main beeper logic
- `inav/src/main/flight/dshot_beeper.h` - DShot beeper API
- `inav/src/main/drivers/pwm_output.c` - DShot command sending

**Arming logic:**
- `inav/src/main/fc/fc_core.c` - Arming state machine
- `inav/src/main/sensors/diagnostics.h` - Arming flags (look for `dshot_beeper`)
- `inav/src/main/fc/runtime_config.h` - Arming conditions

**Configuration:**
- Search for `dshot_beeper` settings
- Check if there's a timeout or condition that should stop beeping

## Key Questions to Answer

1. **When does DShot beeper activate?**
   - Immediately when disarmed?
   - After a timeout when disarmed?
   - When unable to arm?

2. **What is the `dshot_beeper` arming flag?**
   - Why would DShot beeper itself prevent arming?
   - Is this intentional or a bug?

3. **Is there a feedback loop?**
   - Chart: Unable to arm → Beeper activates → Sets arming flag → Prevents arming → Loop

4. **What should the behavior be?**
   - Should DShot beeper respect arming attempts?
   - Should it have a timeout?
   - Should it disable itself when trying to arm?

## Expected Deliverables

**Investigation Report** including:

1. **Code Analysis:**
   - How DShot beeper logic works
   - When it activates and deactivates
   - What triggers continuous beeping

2. **Arming Flag Analysis:**
   - What the `dshot_beeper` arming flag represents
   - Why it prevents arming
   - Whether this is intentional

3. **Feedback Loop Determination:**
   - YES/NO: Is there a circular dependency?
   - If YES: Detailed explanation of the loop
   - Flow diagram showing the circular logic

4. **Root Cause:**
   - Bug or feature?
   - What configuration or condition triggered user's issue?
   - Why turning off DShot beeper fixed it?

5. **Recommendation:**
   - If bug: Proposed fix
   - If configuration issue: What user should do
   - If design flaw: How to improve the logic

## Success Criteria

- [ ] DShot beeper activation logic understood and documented
- [ ] `dshot_beeper` arming flag purpose identified
- [ ] Feedback loop confirmed (YES) or ruled out (NO)
- [ ] Root cause of continuous beeping identified
- [ ] Clear explanation of why disabling beeper allowed arming
- [ ] Recommendation provided (fix, config change, or WAD)
- [ ] Completion report sent to manager

## Reproduction Steps (if applicable)

If a feedback loop is confirmed, provide steps to reproduce:
1. Enable DShot beeper
2. Configure settings to trigger the arming flag
3. Observe continuous beeping
4. Verify unable to arm with `dshot_beeper` flag
5. Disable DShot beeper
6. Verify arming works and beeping stops

## Related

- **Repository:** inav (firmware)
- **Feature:** DShot beeper / Lost aircraft alarm
- **User Report:** Continuous beeping, unable to arm, `dshot_beeper` arming flag

---

**Last Updated:** 2026-01-29

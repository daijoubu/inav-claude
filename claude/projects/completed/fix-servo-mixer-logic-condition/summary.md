# Project: Fix Servo Mixer Logic Condition Activation

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix
**Created:** 2026-01-20
**Assignment:** 📝 Planned
**GitHub Issue:** #11069
**Estimated Time:** 2-4 hours

## Overview

Servo mixer does not respect logic condition activation settings. When a logic condition is selected as the activation parameter for a servo mix, the mix remains active regardless of whether the logic condition is true or false.

## Problem

User reports that servo mixing ignores logic condition state:
- Logic condition is set up and verified working (shows blue dot when true)
- Servo mix is configured to activate based on this logic condition
- **Bug:** Servo mix is always active, regardless of logic condition state
- **Expected:** Mix should only be active when logic condition is true

## Affected Version

- INAV 8.0.1 (user report)
- Status on current version: Unknown (needs verification)

## Objectives

1. Reproduce the issue in SITL or on hardware
2. Identify root cause in servo mixer logic condition handling
3. Fix the logic condition activation check
4. Test fix with various logic condition configurations
5. Verify fix doesn't break existing servo mixer functionality

## Scope

**In Scope:**
- Servo mixer logic condition activation
- Logic condition evaluation in mixer context
- Testing with SITL/hardware verification

**Out of Scope:**
- Other servo mixer features (unless directly related)
- Logic condition system itself (already verified working)
- GUI configurator changes (unless required for fix)

## Implementation Steps

1. Review servo mixer code to understand logic condition integration
2. Find where activation logic condition should be checked
3. Reproduce issue in SITL or with test configuration
4. Identify why logic condition is being ignored
5. Implement fix to properly evaluate logic condition
6. Test with various scenarios (true/false/changing states)
7. Verify existing servo mixer functionality still works
8. Create PR with fix

## Success Criteria

- [ ] Issue reproduced and root cause identified
- [ ] Fix implemented that properly evaluates logic condition
- [ ] Servo mix only active when logic condition is true
- [ ] Servo mix inactive when logic condition is false
- [ ] Logic condition state changes properly activate/deactivate mix
- [ ] Existing servo mixer functionality unaffected
- [ ] Code builds successfully
- [ ] Testing completed (SITL or hardware)
- [ ] PR created targeting maintenance-9.x

## Priority Justification

MEDIUM-HIGH: This is a functional bug affecting users who rely on conditional servo mixing (common for flaps, bomb drops, cargo release, etc.). While not critical to basic flight, it breaks expected functionality and could affect mission operations.

## References

- GitHub Issue: https://github.com/iNavFlight/inav/issues/11069
- User: kolabuzlu
- Hardware: Matek H743 V3
- Version: INAV 8.0.1

# Project: Fix Servo Throttle Mix When Disarmed

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix / Safety Issue
**Created:** 2026-02-08
**Estimated Effort:** 2-4 hours

## Overview

When disarmed, INAV sets the servo throttle mix contribution to 0. This is incorrect when a servo is marked as reversed or has a negative mixer weight — the zero throttle mix value gets inverted, causing the servo to go to full throttle output instead of minimum. The fix should ensure servos always go to their minimum position when disarmed, correctly accounting for reversal and negative weights.

## Problem

- On disarm, servo throttle mix is set to 0
- For reversed servos or negative mixer weights, 0 maps to the maximum end of travel
- This results in **full throttle on disarm** — a safety hazard

## Solution

Modify the disarm logic so that instead of blindly setting throttle mix to 0, it sets the servo output to the correct minimum value, taking into account:
- Servo reversal flag
- Negative mixer weights
- The actual servo min/max endpoints

## Implementation

- Use the `inav-architecture` agent to locate the code that sets servo throttle mix to 0 when disarmed
- Likely in servo mixer code (`src/main/flight/servos.c` or similar)
- Ensure the disarmed output respects reversal and weight sign
- Test with both normal and reversed servo configurations

## Success Criteria

- [ ] Servo goes to minimum output when disarmed (normal configuration)
- [ ] Servo goes to minimum output when disarmed (reversed servo)
- [ ] Servo goes to minimum output when disarmed (negative mixer weight)
- [ ] No behavioral change for non-throttle servo channels
- [ ] Code compiles for SITL and at least one hardware target
- [ ] PR created against `maintenance-9.x`

## Related

- **Assignment:** `manager/email/sent/2026-02-08-task-fix-servo-throttle-mix-disarm.md`

# Project: Hide Motor Direction Radio Box for Fixed Wing

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** UI Fix
**Created:** 2026-02-08
**Estimated Effort:** 1-2 hours

## Overview

The motor direction radio box (normal/reverse) is currently visible for all aircraft types in the configurator. It should be hidden when the aircraft type is fixed wing, as motor direction reversal is not applicable to fixed wing setups.

## Problem

- The normal/reverse motor direction radio buttons are shown for fixed wing aircraft
- This option is not relevant for fixed wing and may confuse users

## Solution

Conditionally hide the motor direction radio box based on the selected aircraft type. When the aircraft type is fixed wing, the radio box should not be rendered or should be hidden.

## Implementation

- Find the motor direction radio box in the configurator UI code
- Add a condition to hide it when aircraft type is fixed wing
- Ensure it remains visible for multirotors and other applicable types

## Success Criteria

- [ ] Motor direction radio box hidden for fixed wing aircraft type
- [ ] Motor direction radio box still visible for multirotor aircraft types
- [ ] No regressions in other aircraft type configurations
- [ ] PR created against `maintenance-9.x` (inav-configurator)

## Related

- **Assignment:** `manager/email/sent/2026-02-08-task-hide-motor-direction-fixed-wing.md`

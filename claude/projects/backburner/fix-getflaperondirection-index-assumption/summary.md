# Project: Fix getFlaperonDirection() Servo-Channel-Number Assumption

**Status:** 📋 TODO
**Priority:** LOW
**Type:** Bug Fix
**Created:** 2026-08-19
**Estimated Time:** 1-3 hours

## Overview

`getFlaperonDirection()` decides flaperon-2 throw direction by checking
whether a servo output is on the conventional channel number, instead of
checking what the mixer is actually doing on that channel.

## Problem

Flagged by developer 2026-08-15 while reviewing servo index semantics on
`feature-dronecan-actuator-control` (mapping compacted servo indices to
DroneCAN `actuator_id`) — not part of that work, just found along the way.

**Location:** `src/main/flight/servos.c:133-140`, `getFlaperonDirection()`

```c
int16_t getFlaperonDirection(uint8_t servoPin)
{
    if (servoPin == SERVO_FLAPPERON_2) {   // == 4, a bare literal
        return -1;
    }
    return 1;
}
```

`SERVO_FLAPPERON_2` is just an enum constant equal to 4 (`servos.h:97`) — a
naming convention for "the channel a flaperon-2 rule is conventionally
configured on," not something tracked or enforced by the mixer. Nothing
ties a `smix` rule's actual function (its `inputSource`) to its
`targetChannel` number — a user is free to configure any rule on any
channel (CLI only validates `0 <= targetChannel < MAX_SUPPORTED_SERVOS`,
`fc/cli.c:2416`).

**Failure scenario:** If a user's servo mixer doesn't follow the
conventional index assignment — e.g. they configure elevator (or anything
else) on channel 4 instead of a flaperon — `getFlaperonDirection()` still
returns -1 for that channel purely because of the index-number coincidence,
silently reversing that servo's throw direction. Real, if narrow,
correctness bug: works by convention/luck, not by checking what's actually
mixed onto that channel.

## Objectives

1. Make flaperon-2 direction detection depend on the actual configured
   mixer rule/function rather than a hardcoded channel-number literal, or
2. If that's not practical, document and validate the assumption instead
   (e.g. warn/reject configs where channel 4 isn't actually a flaperon rule)

## Scope

**In Scope:**
- `src/main/flight/servos.c` (`getFlaperonDirection()` and callers)

**Out of Scope:**
- `feature-dronecan-actuator-control` — unrelated, this was found while
  reviewing that project but doesn't block or depend on it

## Success Criteria

- [ ] Flaperon-2 direction is no longer determined purely by channel number
      (fixed), or the channel-number assumption is documented/validated
      (mitigated)
- [ ] Existing servo mixer tests still pass
- [ ] Completion report sent to manager

## Estimated Time

1-3 hours

## Priority Justification

LOW: narrow edge case (only triggers if a user manually mixes something
other than flaperon-2 onto channel 4), not flight-safety-critical, and no
field reports of it occurring. Backburnered rather than actively assigned.

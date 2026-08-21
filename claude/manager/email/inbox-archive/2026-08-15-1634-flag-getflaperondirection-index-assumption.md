# Flag: getFlaperonDirection() Relies on Servo Channel Number, Not Actual Mixer Rule

**Date:** 2026-08-15 16:34
**From:** Developer
**To:** Manager
**Re:** Bug found during code review, feature-dronecan-actuator-control (not part of current work — flagging for separate tracking)

## Flag

Found while reviewing servo index semantics on feature-dronecan-actuator-control (mapping compacted servo indices to DroneCAN actuator_id).

**Location:** `src/main/flight/servos.c:133-140`, `getFlaperonDirection()`

**Issue:** This function assumes servo channel 4 is always "flaperon 2" and needs its throw direction reversed:

```c
int16_t getFlaperonDirection(uint8_t servoPin)
{
    if (servoPin == SERVO_FLAPPERON_2) {   // == 4, a bare literal
        return -1;
    }
    return 1;
}
```

`SERVO_FLAPPERON_2` is just an enum constant equal to 4 (`servos.h:97`) — a naming convention for "the channel a flaperon-2 rule is conventionally configured on," not something tracked or enforced by the mixer. Nothing ties a `smix` rule's actual function (its `inputSource`) to its `targetChannel` number — a user is free to configure any rule on any channel (CLI only validates `0 <= targetChannel < MAX_SUPPORTED_SERVOS`, `fc/cli.c:2416`).

**Failure scenario:** If a user's servo mixer doesn't follow the conventional index assignment — e.g. they configure elevator (or anything else) on channel 4 instead of a flaperon — `getFlaperonDirection()` still returns -1 for that channel purely because of the index-number coincidence, silently reversing that servo's throw direction. This is a real, if narrow, correctness bug: it works by convention/luck, not by actually checking what's mixed onto that channel.

**Suggestion:** Worth a separate tracked issue to make flaperon-2 direction detection depend on the actual configured rule/function rather than a hardcoded channel-number literal, or otherwise document/validate the assumption. Not something to fix as part of the current DroneCAN actuator-control work — just flagging so it doesn't get lost.

## Blockers

None — this does not block current work.

---
**Developer**

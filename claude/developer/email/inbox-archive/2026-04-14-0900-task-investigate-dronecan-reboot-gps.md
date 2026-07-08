# Task Assignment: Investigate DroneCAN GPS Behavior on FC Reboot

**Date:** 2026-04-14 09:00
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-reboot-gps
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4-8 hours
**Base Branch:** maintenance-10.x

## Task

Investigate why DroneCAN GPS provider stops updating GPS messages when the FC is rebooted without removing power (soft reboot). The GPS provider continues to work after a full power cycle but fails after a soft reboot.

## Background

This is a bug investigation. You've observed that:
- GPS updates work normally through a full power cycle (remove and reapply power)
- GPS updates stop after a software reboot (FC reset without power cycle)
- This suggests the DroneCAN driver may not properly reinitialize or resubscribe to messages after a soft reset

## What to Do

1. **Review DroneCAN initialization code:**
   - How does the DroneCAN driver initialize on startup?
   - Is there any code that handles re-initialization on soft reset?
   - Check for any state that persists across reboots that shouldn't

2. **Check GPS provider registration:**
   - How does a GPS provider register with the navigation system?
   - Is there a mechanism to re-register after reset?
   - Look at `gpsProviderInit()` and related functions

3. **Review DroneCAN node behavior:**
   - How do DroneCAN nodes (e.g., GPS sensor) handle FC reset?
   - Is there heartbeat or connection monitoring?
   - Check for "alive" tracking that may fail to reset

4. **Reproduce and confirm:**
   - Identify exact conditions where failure occurs
   - Document exact symptoms (no position fix? stale data?)

5. **Identify fix if possible:**
   - Document root cause if found
   - Propose solution approach

**Use the inav-architecture agent to find where DroneCAN and GPS provider code lives.**

## Success Criteria

- [ ] Code reviewed for initialization/resume logic
- [ ] Root cause identified (or "unable to determine")
- [ ] Reproduction steps documented
- [ ] Fix recommendation provided
- [ ] Investigation report completed

## Project Directory

`claude/projects/active/investigate-dronecan-reboot-gps/`

---

**Manager**
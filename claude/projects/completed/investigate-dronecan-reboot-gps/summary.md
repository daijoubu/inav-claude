# Project: Investigate DroneCAN GPS Behavior on FC Reboot

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Bug Fix / Testing
**Created:** 2026-04-14
**Estimated Effort:** 4-8 hours

## Overview

Investigate why DroneCAN GPS provider stops updating GPS messages when the flight controller is rebooted without removing power (soft reboot). The GPS provider continues to function normally through a full power cycle but fails to update after a soft reboot.

## Problem

During development testing, if the FC is rebooted (software reset) without removing power, the DroneCAN GPS provider appears to stop sending/updating GPS messages. A full power cycle (remove and reapply power) restores normal operation. This suggests the DroneCAN driver may not properly reinitialize or resubscribe to messages after a soft reset.

## Investigation Steps

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

## Scope

**In Scope:**
- DroneCAN GPS provider behavior on soft reboot
- GPS provider initialization/re-initialization logic
- DroneCAN driver state management

**Out of Scope:**
- Other GPS providers (GPS, SLPort, etc.)
- Full fix implementation (this is investigation only)
- Changes to upstream DroneCAN libraries

## Success Criteria

- [ ] Code reviewed for initialization/resume logic
- [ ] Root cause identified (or "unable to determine")
- [ ] Reproduction steps documented
- [ ] Fix recommendation provided
- [ ] Investigation report completed

## Related

- **Base Branch:** maintenance-10.x
- **Repository:** inavflight/inav
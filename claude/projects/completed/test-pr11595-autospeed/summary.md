# Project: Test PR #11595 - Fixed Wing Auto Speed Mode

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Hardware Testing
**Created:** 2026-05-27
**Estimated Effort:** 1 day (field testing)

## Overview

Field test PR #11595 (breadoven) — Fixed Wing Auto Speed Mode on an actual plane this weekend.

## Problem

New feature needs real-world flight testing before merge. HITL tested only so far.

## Scope

**In Scope:**
- Flash PR #11595 firmware to flight controller
- Test Auto Speed Mode in flight on fixed-wing aircraft
- Verify throttle PID control, speed hold, mode transitions
- Report findings

**Out of Scope:**
- Code review (already done by others)
- Configurator changes

## Success Criteria

- [ ] Firmware builds and flashes successfully
- [ ] Auto Speed Mode activates/deactivates correctly
- [ ] Speed hold is stable in-flight
- [ ] No unexpected behavior during mode transitions
- [ ] Test report sent to manager

## Related

- **PR:** [#11595](https://github.com/iNavFlight/inav/pull/11595)
- **Configurator PR:** [#2641](https://github.com/iNavFlight/inav-configurator/pull/2641)

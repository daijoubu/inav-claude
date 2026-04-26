# Project: Test STM32F7xx HAL v1.3.3 Update

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Testing / Validation
**Created:** 2026-04-20
**Estimated Effort:** 1-2 hours

## Overview

Hardware validation of the `feature/stm32f7-hal-v1.3.3-update` branch on a MATEKF765SE. The HAL upgrade, macro redefinition fixes, and DroneCAN driver port are all complete — this project validates the result on real hardware before a PR is opened.

## Problem

The STM32F7xx HAL has been upgraded from v1.2.2 to v1.3.3. All build-level issues are resolved, but hardware behaviour (especially DroneCAN) has not yet been validated.

## Solution

Flash the branch to a MATEKF765SE and run through the hardware validation checklist from the developer's plan: DroneCAN battery monitor, error recovery states, and SD card baseline tests.

## Implementation

Phase 5 of the developer plan (`claude/manager/email/inbox/2026-04-15-1855-plan-dronecan-hal-v1.3.3-port.md`):

1. Build MATEKF765 target — verify zero compilation errors
2. Flash to MATEKF765SE
3. Verify DroneCAN battery monitor detected (voltage/current data)
4. Test CAN error recovery (BUS_OFF, ERROR_PASSIVE states)
5. Run baseline SD card tests for regression check

## Success Criteria

- [ ] MATEKF765SE build: zero errors, zero warnings
- [ ] DroneCAN battery monitor detected and reporting voltage/current
- [ ] CAN error recovery states behave correctly
- [ ] Baseline SD card tests pass (no regressions)
- [ ] PR opened against `maintenance-10.x`

## Related

- **Branch:** `feature/stm32f7-hal-v1.3.3-update`
- **Predecessor:** `fix-stm32f7-hal-redefinition-warnings` (completed 2026-04-20)
- **Developer plan:** `claude/manager/email/inbox/2026-04-15-1855-plan-dronecan-hal-v1.3.3-port.md`
- **Repository:** inav (firmware) | **PR Target:** `maintenance-10.x` (HAL upgrade is a breaking change)
- **Assignment:** `manager/email/sent/2026-04-20-2030-task-test-stm32f7-hal-v1.3.3-update.md`
- **PR:** [#11514](https://github.com/iNavFlight/inav/pull/11514) — Open against `maintenance-10.x`
- **Completed:** 2026-04-25

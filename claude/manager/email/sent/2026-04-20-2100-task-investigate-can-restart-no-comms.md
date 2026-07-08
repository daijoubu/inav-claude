# Task Assignment: Investigate CAN Network No-Comms After INAV Restart

**Date:** 2026-04-20 21:00
**From:** Manager
**To:** Developer
**Project:** investigate-can-restart-no-comms
**Priority:** MEDIUM-HIGH (after HAL testing)
**Estimated Effort:** 3-5 hours

## Task

Investigate why CAN peripherals stop communicating after INAV is restarted without power-cycling the whole network. The FC comes back up but CAN devices (e.g. DroneCAN battery monitor) appear dead until everything is power-cycled.

## Background

This is the issue you observed during HAL testing: when you reboot the FC without power-cycling the DroneCAN battery monitor, communication doesn't resume. A full power cycle restores normal operation.

This should be addressed after the HAL v1.3.3 validation is complete.

## What to Do

1. Read `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c` — focus on init and start sequence
2. Check whether `HAL_CAN_Start()` alone issues a bus reset or whether explicit dominant/recessive sequencing is needed
3. Review DroneCAN node allocation table reset on firmware init
4. Check if ERROR_PASSIVE / BUS_OFF recovery logic is present and triggered correctly
5. Reproduce on bench: reboot FC without power-cycling DroneCAN battery monitor, confirm no comms
6. Implement fix and verify comms resume without power cycle

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Bench reproduction confirmed (reboot → no comms)
- [ ] Fix implemented
- [ ] After fix: FC reboot restores CAN comms without power-cycling peripherals
- [ ] No regression on normal power-on behaviour
- [ ] PR opened against `maintenance-10.x`

## Project Directory

`claude/projects/active/investigate-can-restart-no-comms/`

## Notes

- Branch: Create new branch off `maintenance-10.x` (separate from HAL update branch)
- PR Target: `maintenance-10.x`

---
**Manager**
# Project: Investigate CAN Network No-Comms After INAV Restart

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation
**Created:** 2026-04-20
**Estimated Effort:** 3-5 hours

## Overview

Investigate why CAN peripherals stop communicating after INAV is restarted without power-cycling the whole network. The FC comes back up but CAN devices (e.g. DroneCAN battery monitor) appear dead until everything is power-cycled.

## Problem

When INAV is restarted (e.g. via CLI `reboot` or configurator reconnect) without also power-cycling connected CAN devices, communication with those peripherals does not resume. The user has no CAN analyser in the field, so the failure mode is observable only as missing peripheral data (battery voltage/current absent). A full power cycle restores normal operation.

Likely root causes to investigate:
- CAN bus not properly reset on firmware init — peripheral may be in BUS_OFF or ERROR_PASSIVE state from the previous session and waiting for the FC to recover it
- HAL CAN start sequence on `canardSTM32Init()` not re-asserting dominant state to wake sleeping nodes
- DroneCAN node IDs or session state not renegotiated on restart, causing ID conflicts or stale allocation table

## Solution

Audit the CAN initialisation path in `canard_stm32f7xx_driver.c` and DroneCAN node allocation logic. Determine whether a proper bus reset (128+ recessive bits) is issued on startup, and whether peripheral node state needs to be cleared. Propose and implement a fix.

## Scope

**In Scope:**
- CAN peripheral init sequence in firmware
- DroneCAN node allocation / session restart behaviour
- Bus error state recovery on FC reboot
- SITL or bench testing with a DroneCAN device

**Out of Scope:**
- Changes to third-party CAN devices
- CAN timing / bitrate configuration

## Implementation

1. Read `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c` — focus on init and start sequence
2. Check whether `HAL_CAN_Start()` alone issues a bus reset or whether explicit dominant/recessive sequencing is needed
3. Review DroneCAN node allocation table reset on firmware init (`src/main/drivers/dronecan/`)
4. Check if ERROR_PASSIVE / BUS_OFF recovery logic is present and triggered correctly
5. Reproduce on bench (MATEKF765SE + DroneCAN battery monitor): reboot FC without power-cycling monitor, confirm no comms
6. Implement fix and verify comms resume without power cycle

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Bench reproduction confirmed (reboot → no comms)
- [ ] Fix implemented
- [ ] After fix: FC reboot restores CAN comms without power-cycling peripherals
- [ ] No regression on normal power-on behaviour
- [ ] PR opened against `maintenance-10.x`

## Related

- **Branch:** New branch off `maintenance-10.x` (not the HAL update branch)
- **Repository:** inav (firmware) | **PR Target:** `maintenance-10.x`
- **Assignment:** `manager/email/sent/2026-04-20-2100-task-investigate-can-restart-no-comms.md`
- **Reported by:** User (field observation — no CAN analyser available)

# Task Completed: fix/h7-dronecan-driver — Branch Complete, Parked for Review

**Date:** 2026-05-29 17:53
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Branch fix/h7-dronecan-driver has been completed and pushed to GitHub. Three rounds of code review were conducted and all actionable findings addressed. Both F7 (MATEKF765SE) and H7 (KAKUTEH7WING) targets build cleanly and have been tested on hardware.

## Branch and Commits

**Branch:** `fix/h7-dronecan-driver`
**Status:** Pushed to GitHub, awaiting upstream PR review

## Changes Made

### H7 FDCAN driver (canard_stm32h7xx_driver.c)
- Fixed FDCAN clock source: was using APB1 (HAL_RCC_GetPCLK1Freq), now correctly uses HAL_RCCEx_GetPeriphCLKFreq(RCC_PERIPHCLK_FDCAN)
- Reduced SJW from 8 to 1 (HAL handles +1 offset; verified at 1Mbps)
- Disabled AutoRetransmission (was filling 32-slot TX FIFO on degraded bus)
- Set TxBuffersNbr to 0 (driver uses FIFO queue only, dedicated buffers were unused)
- Added TXBCR flush before clearing CCCR.INIT on bus-off recovery
- Added PLL2 config return value check with Error_Handler on failure

### F7 bxCAN driver (canard_stm32f7xx_driver.c)
- Restored SJW=3 (register value; hardware SJW=4 tq — wider SJW needed vs H7 FDCAN)
- Disabled AutoRetransmission
- Added return value check for canardSTM32ComputeTimings
- Removed log spam from TX failure and timing calculation paths

### DroneCAN state machine (dronecan.c)
- Added STATE_DRONECAN_FAILED — set on CAN peripheral init failure
- Added STATE_DRONECAN_COUNT sentinel with STATIC_ASSERT protecting CLI name array
- Increased bus-off recovery delay from 1ms to 20ms (worst-case 128×11 recovery is 11.264ms at 125kbps)
- Moved protocol status check to 1Hz in NORMAL state (was ~500Hz)
- Moved protocol status check inside 20ms recovery cadence in BUS_OFF state
- GPS provider guard moved to dispatch layer in dronecan.c (was duplicated in 3 gps_dronecan.c leaf functions); also added to handle_GNSSRCTMStream which had no guard
- Conditional CAN status logging (only logs when BusOff or ErrorPassive is non-zero)

### PLL2 clock configuration (system_stm32h7xx.c)
- Expanded PLL2 block from USE_SDCARD_SDIO only to USE_SDCARD_SDIO || USE_DRONECAN
- Changed PLL2Q from 3 (266MHz, invalid for FDCAN) to 10 (80MHz)
- Added STATIC_ASSERT for HSE_VALUE divisibility
- Added HAL_RCCEx_PeriphCLKConfig return value check

### GPS DroneCAN driver (gps_dronecan.c)
- Fixed GPS provider leakthrough: DroneCAN fix messages were written to gpsSolDRV regardless of configured GPS provider
- Added NaN guard for GNSSAuxiliary HDOP field (DroneCAN float16 optional fields encode NaN when unpopulated)
- Added gpsConstrainHDOP() clamping to prevent uint16_t overflow for extreme DOP values
- Removed lastVDOP (dead store — no vdop field in gpsSol, not EPV-compatible)
- Removed stale UNUSED(pgnssAux) macro and placeholder comment

### KAKUTEH7WING target
- Added USE_DRONECAN with CAN1_RX/TX pin definitions (PD0/PD1)

### CLI (cli.c)
- Added FAILED to dronecanStateNames array
- Added STATIC_ASSERT to keep array size in sync with enum
- Added bounds clamp before state name lookup

## Testing

- [x] F7 (MATEKF765SE) builds cleanly
- [x] H7 (KAKUTEH7WING) builds cleanly
- [x] Hardware tested on both targets
- [x] Code review completed (3 rounds)
- [x] All actionable findings addressed

## Known Outstanding Issue — Requires Separate Project

**F7 permanent BUS_OFF lock**: On STM32F7 targets, ESR.BOFF (CAN_FLAG_BOF) is a sticky read-only flag that is NOT cleared when AutoBusOff=ENABLE completes the 128×11 recovery sequence. canardSTM32RecoverFromBusOff() on F7 is currently a no-op (documented TODO). An attempt to fix this with HAL_CAN_Stop/Start caused a full FC lockup when called from the scheduler context with CAN interrupts active. The correct fix requires a safe mechanism to re-enter init mode (clearing ESR.BOFF) without blocking the scheduler — likely direct MCR/MSR register manipulation with a timeout, or deferring the operation to a lower-priority task. Please create a project to track this investigation.

## Next Steps

The branch is ready for upstream PR review when you are satisfied with the scope.

---
**Developer**

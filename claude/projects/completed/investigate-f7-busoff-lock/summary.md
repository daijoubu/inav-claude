# Project: Investigate F7 Permanent BUS_OFF Lock

**Status:** ✅ COMPLETED (2026-05-30)
**Priority:** MEDIUM-HIGH
**Type:** Bug Investigation / Fix
**Created:** 2026-05-29
**Completed:** 2026-05-30

## Overview

`canardSTM32RecoverFromBusOff()` in the F7 bxCAN driver is a no-op. This is intentional — the function exists as an API requirement shared with the H7 FDCAN driver, which does require explicit software action to recover from Bus-Off. Whether the F7 bxCAN hardware also requires software intervention (or handles recovery automatically via ABOM) has not been confirmed against the STM32F7 reference manual.

## Problem

It is unclear whether the F7 bxCAN peripheral requires any software action to recover from Bus-Off, or whether ABOM (Automatic Bus-Off Management) handles it fully in hardware. The no-op implementation may be correct as-is, or it may be masking a real recovery gap. This needs to be confirmed before any fix is attempted.

## Objectives

1. Confirm via STM32F7 RM whether bxCAN ABOM clears ESR.BOFF automatically after recovery
2. Determine whether `canardSTM32RecoverFromBusOff()` being a no-op is correct or a gap
3. If action is required: design and implement a safe recovery mechanism

## Scope

**In Scope:**
- STM32F7 bxCAN driver only (`canard_stm32f7xx_driver.c`)
- ESR.BOFF flag clearing after AutoBusOff hardware recovery
- Safe execution context (defer to low-priority task or use non-blocking register poll)

**Out of Scope:**
- H7 FDCAN driver (handled separately in `fix/h7-dronecan-driver`)
- bxCAN on F4 targets (separate driver)

## Outcome

Verdict: **no-op is correct.** RM0410 §40.7.6 confirms that with `CAN_MCR.ABOM=1` (set in `canardSTM32CAN1_Init`), hardware automatically exits bus-off after 128×11 recessive bits by cycling `INRQ` and clearing `ESR.BOFF`. No software intervention is needed. Comment in `canardSTM32RecoverFromBusOff()` updated with RM0410 citations. Change shipped as part of PR #11607 (draft, `fix/h7-dronecan-driver` → `maintenance-10.x`).

## Success Criteria

- [x] STM32F7 RM reviewed: ABOM behaviour and ESR.BOFF clearing confirmed
- [x] Verdict documented: no-op is correct, rationale in `findings.md` and source comment
- [x] No implementation required — hardware handles recovery fully
- [x] Comment updated in PR #11607

## Related

- **Branch:** `fix/h7-dronecan-driver`
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`
- **Flagged by:** Developer in completion report for `fix/h7-dronecan-driver` (2026-05-29)
- **Hardware:** MATEKF765SE (STM32F765)
- **Reference:** `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`

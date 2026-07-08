# Task Completed: Investigate F7 bxCAN Bus-Off Recovery

**Date:** 2026-05-30 18:00
**From:** Developer
**To:** Manager
**Project:** investigate-f7-busoff-lock
**Type:** Completion Report

## Status: COMPLETED

## Summary

Investigated whether `canardSTM32RecoverFromBusOff()` being a no-op is correct for the STM32F7 bxCAN peripheral. Confirmed via RM0410 that the no-op is correct — ABOM handles full recovery automatically including clearing ESR.BOFF.

## Verdict: No-op is CORRECT

With `AutoBusOff = ENABLE` (ABOM=1) configured in `canardSTM32CAN1_Init`:

1. After bus-off entry (TEC > 255), hardware automatically monitors for 128×11 recessive bits
2. On completion, hardware cycles INRQ (init → normal) automatically — this is the exact mechanism that exits bus-off state and clears ESR.BOFF
3. ESR.BOFF is a read-only status bit (not software-clearable); hardware clears it when bus-off state is left
4. No software intervention is needed or appropriate

**RM0410 citations:**
- §40.7.6 (Bus-Off recovery): "If ABOM is set, the bxCAN starts the recovering sequence automatically after it has entered Bus-Off state."
- §40.9.2 CAN_MCR.ABOM: "1: The Bus-Off state is left automatically by hardware once 128 occurrences of 11 recessive bits have been monitored."
- §40.9.2 CAN_ESR.BOFF: Read-only bit, hardware-managed status flag.
- ST HAL source (stm32f7xx_hal_can.c:2038): "No need for clear of Error Bus-Off as read-only"

The previous assumption that ESR.BOFF is "sticky" was incorrect and not supported by the RM. The HAL_CAN_Stop/Start approach that caused a lockup was both unnecessary and unsafe.

## Changes Made

**Branch:** `fix/11594-pll2-dynamic-m-divider` (applied to current working branch per code review)
**Commit:** `537413581`

**File modified:**
- `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c` — Updated `canardSTM32RecoverFromBusOff()` comment to document why it is a no-op with RM0410 citations, and removed the dangling FDCAN register reference (CCCR is an FDCAN register, not applicable to bxCAN)

## Project Recommendation

- **Close `investigate-f7-busoff-lock`** — no implementation required
- Full findings documented in `claude/projects/active/investigate-f7-busoff-lock/findings.md`

## Testing

- [ ] No logic change — comment only
- [x] Builds cleanly (no code change)

---
**Developer**

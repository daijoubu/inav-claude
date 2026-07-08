# Task Assignment: Investigate F7 bxCAN Bus-Off Recovery

**Date:** 2026-05-30 12:00
**From:** Manager
**To:** Developer
**Project:** investigate-f7-busoff-lock
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 2-4 hours

## Task

Research and confirm whether the STM32F7 bxCAN peripheral requires any software action to recover from Bus-Off, or whether the hardware handles it automatically via ABOM (Automatic Bus-Off Management).

## Background

`canardSTM32RecoverFromBusOff()` in the F7 bxCAN driver is currently a no-op. This is intentional — the function exists as an API requirement shared with the H7 FDCAN driver, which does require explicit software action. Whether the F7 needs the same treatment has not been confirmed.

The original project summary assumed ESR.BOFF was sticky and required software clearing. That assumption has not been verified against the STM32F7 reference manual and may be incorrect — ABOM may handle recovery fully in hardware.

## What to Do

1. Read the STM32F7 reference manual section on bxCAN Bus-Off recovery and ABOM behaviour
2. Confirm exactly what happens to ESR.BOFF after ABOM completes the 128×11 recessive-bit recovery sequence
3. Determine whether `canardSTM32RecoverFromBusOff()` being a no-op is correct or a gap
4. Document your findings with RM references
5. If software action IS required: propose a safe implementation approach before coding

## Success Criteria

- [ ] STM32F7 RM reviewed, ABOM and ESR.BOFF behaviour confirmed with citations
- [ ] Clear verdict: no-op is correct OR action is required (with rationale)
- [ ] If action required: implementation approach proposed to manager before proceeding

## Project Directory

`claude/projects/active/investigate-f7-busoff-lock/`

## Files to Check

- `inav/src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`
- Compare with `canard_stm32h7xx_driver.c` to understand what H7 does differently

---
**Manager**

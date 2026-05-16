# Project: Verify and Update STM32H7xx HAL and CMSIS

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Verification / Maintenance
**Created:** 2026-02-20
**Estimated Effort:** 4-8 hours

## Overview

Determine current STM32H7xx HAL and CMSIS versions and update if more than 2 versions behind latest (V1.11.5). H7xx HAL appears to be more recent than F7xx/F4xx based on file structure but version needs verification.

## Problem

H7xx HAL version is unknown. Need to:
1. Determine current HAL version
2. Determine current CMSIS version
3. Assess gap from latest releases
4. Update if significant gap exists

## Solution

1. Check version markers in HAL headers
2. Compare with latest STM32CubeH7 release
3. Update HAL and CMSIS if > 2 versions behind
4. Verify H7-specific workarounds still needed

## Scope

**In Scope:**
- HAL version verification
- CMSIS version verification
- Update if needed
- Verify HSE workarounds

**Out of Scope:**
- F7xx or F4xx updates (separate tasks)

## Success Criteria

- [ ] Current HAL version documented
- [ ] Current CMSIS version documented
- [ ] Decision made: update or skip
- [ ] If updated: firmware builds and tests pass

## H7-Specific Workarounds to Verify

INAV has H7-specific workarounds that may need adjustment:
- `USE_H7_HSERDY_SLOW_WORKAROUND` - HSE ready >10s issue
- `USE_H7_HSE_TIMEOUT_WORKAROUND` - Force reset on HSE timeout
- `HandleStuckSysTick()` - SysTick recovery

## Related

- **Assessment:** `completed/assess-stm32-hal-updates/`
- **F7xx Update:** `active/update-stm32f7-hal/`
- **F4xx Update:** `active/update-stm32f4-hal/`
- **Source:** STM32CubeH7 (https://github.com/STMicroelectronics/STM32CubeH7)

## Directory

`active/verify-stm32h7-hal/`
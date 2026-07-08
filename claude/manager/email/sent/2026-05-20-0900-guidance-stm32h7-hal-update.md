# Guidance: STM32H7 HAL Update - Build Verification

**Date:** 2026-05-20 09:00
**From:** Manager
**To:** Developer
**Re:** STM32H7xx HAL Update (project: update-stm32h7-hal)

## Guidance

The HAL update on the `fix/stm32h7-hal-v1.13.0-update` branch needs additional verification before we can mark this complete.

## What to Do

1. **Build all CI H7 targets** — Build all H7 targets (not just MATEKH743) to confirm clean compilation with HAL V1.11.6 / CMSIS V1.10.7
2. **Check INAV-specific patches** — Review git history for any INAV-specific modifications to HAL/CMSIS files and ensure they're preserved in the update
3. **Review the 3 H7 workarounds** in system_stm32h7xx.c — verify they're still needed with the new HAL version

## Rationale

We need to be sure the update doesn't break any H7 target before creating a PR and merging.

## Project Directory

`claude/projects/active/update-stm32h7-hal/`

---
**Manager**

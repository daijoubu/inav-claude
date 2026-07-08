# Task Assignment: Fix BOOTLOADER Targets Without Storage Backend

**Date:** 2026-04-28 12:00
**From:** Manager
**To:** Developer
**Project:** fix-bootloader-targets-no-storage
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Five INAV firmware targets have `BOOTLOADER` enabled in their target config but no storage backend (no flash chip or SD card support). This silently produces broken `_bl` binaries that will not function for OTA firmware updates. Investigate the root cause for each target and apply the correct fix.

**Affected targets:**
- ANYFC
- CLRACINGF4AIR
- FF_F35_LIGHTNING
- FLYINGRCF4WINGMINI_NOT_RECOMMENDED
- AIRBOTF7

## Background

This was discovered during the STM32F4 HAL investigation. The `STM32F4xx_HAL_Driver` turned out to be vestigial (F4 uses StdPeriph, not HAL), so no HAL update is needed — but you found this latent bug in the process. Good catch.

## What to Do

1. Check upstream INAV issue tracker for any existing reports on these targets
2. Use `git log` on each target's config to understand when `BOOTLOADER` was added and why
3. Determine if each target's hardware actually supports storage (flash chip, SD slot)
4. For each target, choose the correct fix:
   - **Remove `BOOTLOADER`** if the hardware has no storage and there's no intent to add it
   - **Add storage backend** (`USE_FLASH_*`) if the hardware does have a flash chip
   - **Add compile-time guard** for `MSP_FIRMWARE_UPDATE` if it should require storage
5. Verify `_bl` binaries build correctly for any targets that retain BOOTLOADER support
6. Create a PR targeting `maintenance-10.x`

## Success Criteria

- [ ] Root cause confirmed for all 5 targets
- [ ] Correct fix applied per target
- [ ] `_bl` binaries build successfully for retained BOOTLOADER targets
- [ ] All affected targets compile cleanly
- [ ] PR created targeting `maintenance-10.x`
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/fix-bootloader-targets-no-storage/`

## Branch

New branch off `maintenance-10.x` → PR targets `maintenance-10.x`

---
**Manager**

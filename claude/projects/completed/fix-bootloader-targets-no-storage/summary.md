# Project: fix-bootloader-targets-no-storage

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Bug Fix / Investigation
**Created:** 2026-04-28
**Estimated Effort:** 2-4 hours
**Completed:** 2026-04-28

## Overview

Five targets have `BOOTLOADER` enabled in their target config but no storage backend (FLASH or SD card). This silently produces broken `_bl` binaries that will not function. Discovered during the STM32F4 HAL investigation.

## Problem

The following targets define `BOOTLOADER` without any storage backend, causing silent build failures for `_bl` firmware variants:

- ANYFC
- CLRACINGF4AIR
- FF_F35_LIGHTNING
- FLYINGRCF4WINGMINI_NOT_RECOMMENDED
- AIRBOTF7

These targets compile but produce non-functional bootloader binaries with no upgrade mechanism — a silent bug that wastes user effort when attempting OTA firmware updates.

## Open Questions

1. Why do these 5 targets have `BOOTLOADER` set without storage? Historical artifact or intentional?
2. Should `MSP_FIRMWARE_UPDATE` be made conditional on storage availability (i.e., compile-guarded)?
3. Is this a known upstream issue already being tracked?

## Solution

Investigate each target and determine the correct fix:
- Option A: Remove `BOOTLOADER` from targets that have no storage and no intent to add it
- Option B: Add appropriate storage backend (`USE_FLASH_*` or `USE_SDCARD`) if hardware supports it
- Option C: Add a compile-time guard so `BOOTLOADER`/`MSP_FIRMWARE_UPDATE` requires a storage backend

## Success Criteria

- [ ] Root cause confirmed for all 5 targets (historical mistake vs. intentional)
- [ ] Correct fix applied per target
- [ ] `_bl` binaries build successfully for any targets that retain BOOTLOADER support
- [ ] Compile guard added if appropriate
- [ ] PR created targeting `maintenance-10.x` (or `maintenance-9.x` if backport warranted)

## Outcome

Added `NO_BOOTLOADER` cmake flag (modelled on existing `DISABLE_MSC` pattern) to `cmake/stm32.cmake`. Applied to all 9 affected build targets across 7 directories. CI gap noted: `_bl` variants are excluded from `ninja ci` so this class of bug is invisible to automated builds.

## Related

- **Issue:** [#11521](https://github.com/iNavFlight/inav/issues/11521)
- **PR:** [#11522](https://github.com/iNavFlight/inav/pull/11522) — OPEN (awaiting upstream review)
- **Branch:** `fix-bootloader-targets-no-storage` off `maintenance-9.x`
- **Discovered by:** Developer during `update-stm32f4-hal` investigation
- **Parent investigation:** `completed/update-stm32f4-hal/`

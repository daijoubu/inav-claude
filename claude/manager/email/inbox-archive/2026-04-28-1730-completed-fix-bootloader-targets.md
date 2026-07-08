# Task Completed: Fix BOOTLOADER Targets Without Storage Backend

**Date:** 2026-04-28 17:30
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Nine build targets across 7 target directories had `BOOTLOADER` enabled via their MCU family cmake function but no storage backend (`USE_FLASHFS`/`USE_SDCARD`) defined in target.h. This silently produced `_bl`/`_for_bl`/`_with_bl` firmware variants that compile but cannot function for OTA firmware updates at runtime. The fix adds a `NO_BOOTLOADER` cmake flag (following the existing `DISABLE_MSC` pattern) and sets it on all affected targets.

## Investigation Findings

- Root cause: `target_stm32f405xg` and `target_stm32f7xx` unconditionally pass `BOOTLOADER` to cmake. 80 of 84 STM32F405xg targets correctly have storage defined; these 5 target dirs (covering 9 targets) do not.
- CI never catches this because `_bl` variants are not in `VALID_TARGETS` and are therefore never built by `ninja ci`.
- The storage absence may be an oversight (missing `USE_FLASHFS` definition) rather than a hardware limitation — left open for future contributors to investigate.
- A GitHub issue was filed first: https://github.com/iNavFlight/inav/issues/11521

## Branch and Commits

**Branch:** `fix-bootloader-targets-no-storage` (off upstream/maintenance-9.x)
**PR:** https://github.com/iNavFlight/inav/pull/11522
**Commits:**
- `eb9c9ce74` - fix: disable bootloader variants for targets without storage backend

## Changes Made

**Files modified:**
- `cmake/stm32.cmake` — add `NO_BOOTLOADER` boolean to cmake_parse_arguments; guard bootloader build with `AND NOT args_NO_BOOTLOADER`
- `src/main/target/ANYFC/CMakeLists.txt` — add NO_BOOTLOADER
- `src/main/target/CLRACINGF4AIR/CMakeLists.txt` — add NO_BOOTLOADER to V1/V2/V3
- `src/main/target/FF_F35_LIGHTNING/CMakeLists.txt` — add NO_BOOTLOADER to FF_F35_LIGHTNING and WINGFC
- `src/main/target/FLYINGRCF4WINGMINI_NOT_RECOMMENDED/CMakeLists.txt` — add NO_BOOTLOADER
- `src/main/target/AIRBOTF7/CMakeLists.txt` — add NO_BOOTLOADER to AIRBOTF7 and OMNIBUSF7NANOV7

## Testing

- [x] FF_F35_LIGHTNING builds successfully (release target smoke test)
- [x] ANYFC builds successfully
- [x] ANYFC_bl correctly no longer exists as a build target
- [x] MATEKF765SE builds with bootloader support intact (regression check)

## Lock

- [x] Released inav.lock

---
**Developer**

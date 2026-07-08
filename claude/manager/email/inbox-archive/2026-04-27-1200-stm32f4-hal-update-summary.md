# Status Update: STM32F4 HAL Driver — Investigation Complete

**Date:** 2026-04-27 12:00 (updated)
**From:** Developer
**To:** Manager
**Re:** STM32F4 HAL Update Investigation

## Conclusion: No Value in Updating the F4 HAL

Further investigation shows the `STM32F4xx_HAL_Driver` is **not actually used** by the INAV F4 build. It is vestigial — present in the repo but never compiled:

- It does not appear in `STM32F4_INCLUDE_DIRS` in `cmake/stm32f4.cmake`
- No source files from it are listed in any F4 cmake target
- `config_streamer_stm32f4.c` uses StdPeriph flash functions (`FLASH_Unlock()`, `FLASH_Sector_X`, etc.), not HAL functions (`HAL_FLASH_Unlock()` etc.)
- The compile definitions include `USE_STDPERIPH_DRIVER`, not `USE_HAL_DRIVER`

The F4 family uses the StdPeriph library for all peripherals including flash. The HAL driver directory can potentially be removed from the repo entirely.

**The previous report was incorrect** — the `STM32F4xx_HAL_Driver` is not providing the flash storage backend, and the F4 has no CAN driver in INAV. There is no value in updating it.

## Separate Finding: Latent Bootloader Build Bug

The build failure seen during investigation (`#error No storage backend available` in `src/main/fc/firmware_update_common.c:18`) is a **pre-existing latent bug**, not caused by the HAL removal.

**Background:** `cmake/stm32f4.cmake` and `cmake/stm32f7.cmake` unconditionally set `BOOTLOADER` for all F405 and F7xx targets respectively. This causes cmake to generate a `_bl` bootloader binary for every such target, compiled with `MSP_FIRMWARE_UPDATE` defined. `firmware_update_common.c` then requires either `USE_FLASHFS` or `USE_SDCARD` to be defined — if neither is present, the build fails with `#error No storage backend available`.

**Scale:** 161 targets have `BOOTLOADER` enabled (84 × F405, 77 × F7; H7 and AT32 are commented out).

**Affected targets — 5 have no storage backend:**

| Target | MCU |
|---|---|
| `ANYFC` | STM32F405 |
| `CLRACINGF4AIR` | STM32F405 |
| `FF_F35_LIGHTNING` | STM32F405 |
| `FLYINGRCF4WINGMINI_NOT_RECOMMENDED` | STM32F405 |
| `AIRBOTF7` | STM32F7 |

These targets silently produce unbuildable `_bl` binaries. The other 156 targets are unaffected (they have `USE_FLASHFS` or `USE_SDCARD`).

## Open Questions (Needs Further Investigation)

1. **Why do these 5 targets have `BOOTLOADER` set?** `ANYFC`, `CLRACINGF4AIR` etc. have no external flash and no SD card — MSP firmware update over USB would have nowhere to store firmware update metadata. Were these targets ever intended to support the bootloader, or was `BOOTLOADER` added unconditionally by mistake?

2. **Should `MSP_FIRMWARE_UPDATE` be conditional?** Currently it is always set for any target with `BOOTLOADER`. It may need to be conditional on `USE_FLASHFS` or `USE_SDCARD` being present.

3. **Is this a known upstream issue?** Worth checking if iNavFlight/inav master has the same problem or if it was fixed there.

## Recommended Next Steps

1. Investigate `MSP_FIRMWARE_UPDATE` and the `BOOTLOADER` define for these 5 targets — determine correct fix (remove `BOOTLOADER` from targets that can't support it, or make `MSP_FIRMWARE_UPDATE` conditional on storage availability)
2. Consider whether `STM32F4xx_HAL_Driver` should be removed from the repo as dead code
3. No F4 HAL update work is needed

---
**Developer**

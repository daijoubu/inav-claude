# Project: Investigate F765/H743 Arming Lockup

**Status:** 🚧 IN PROGRESS
**Priority:** HIGH
**Type:** Investigation / Bug Analysis
**Created:** 2026-02-21
**Updated:** 2026-02-21
**Estimated Effort:** 8-16 hours

## Overview

Investigate intermittent FC lockup/freeze at arming time, primarily affecting F765 and H743 flight controllers. Multiple users have reported this issue since INAV 8.0.0, with the problem appearing to involve GPS fix timing, blackbox logging, and possibly DMA/interrupt conflicts.

## Related Issues

| Issue | Title | Hardware | Key Symptom |
|-------|-------|----------|-------------|
| #11299 | Outputs lockup after GPS fix at arming | H743, F765 | Servo jitter at GPS fix, then lockup |
| #10586 | Matek F765 freezing when arming | F765-WSE | 4/5 arm attempts freeze, SD corruption |
| #10646 | Random freeze after time | F7xx | Freeze after random duration |
| #10659 | F7 lockup | F7xx | Related lockup |
| #10800 | F7/H7 issue | F7/H7 | Related issue |
| #11007 | F765 lockup in flight (trackback) | F765 | Freeze at trackback waypoint, log stops |

### Issue #11007 Deep Dive

**Scenario:** F765 locked up during failsafe trackback recovery, exactly when reaching the last trackback waypoint (50m from home).

**Key Evidence:**
- Blackbox log stopped recording at exact moment of lockup
- OSD link quality indicator kept flashing (hardware timer, not FC code)
- Motor shutdown, telemetry stopped, RC control not returned
- FC didn't reboot - remained frozen
- HITL testing could NOT reproduce (no real SD card timing)
- `navState 38` (Trackback) in log at freeze moment

**Analysis:** This appears to be the **same root cause**:
1. Navigation state transition at trackback endpoint
2. Blackbox writes state change to SD card
3. SD card in error state triggers blocking `HAL_SD_Init()`
4. FC freezes in reset loop
5. OSD chip timer continues (hardware-driven, independent of FC)

**Why HITL couldn't reproduce:** breadoven used an **F411 board** for HITL testing. F411 uses SPI-based SD card driver, NOT the SDMMC/SDIO HAL driver. The blocking `HAL_SD_Init()` issue only affects F7/H7 boards that use the rewritten SDMMC driver. To reproduce, HITL testing would need an actual F765 or H743 board.

## Problem Summary

**Symptoms:**
- FC completely freezes at moment of arming
- Servos/motors become unresponsive
- OSD frozen, telemetry stops
- No blackbox log created for failed arm
- Power cycle required to recover
- Intermittent: 2-80% failure rate depending on user

**Affected Hardware:**
- Matek F765-WSE (primary)
- Other F765 boards
- H743 boards (less frequent)
- NOT reported on F4xx or other MCUs

**Timeline:**
- Works fine in INAV 7.1.2
- Problem started in INAV 8.0.0
- Persists through 8.0.x and 9.0.x

**Potential Triggers:**
1. GPS 3D fix acquisition
2. Blackbox logging initialization
3. SD card operations
4. Arming sequence timing

---

## Investigation Findings (2026-02-21)

### Root Cause Identified: F7 SDIO HAL Rewrite

**Commit:** `3561feeb9` (Dec 10, 2024) by mmosca
**Change:** "f7: use hal for sdio"
- Deleted 1603 lines of custom F7 SDIO code (`sdmmc_sdio_f7xx.c`)
- Replaced with HAL-based implementation (`sdmmc_sdio_hal.c`)

### The Freeze Mechanism

```
1. User waits for GPS fix
              ↓
2. GPS fix triggers AHRS/DMA activity
   → Servo jitter observed
   → SD card may enter error state
              ↓
3. User arms
   → blackboxStart() called (fc_core.c:894)
   → AFATFS needs SD card
              ↓
4. SD card in error state
   → sdcardSdio_reset() called
   → HAL_SD_Init() BLOCKS (up to 100s of ms)
              ↓
5. If still failing → goto doMore loop
   → Repeated blocking HAL_SD_Init() calls
   → FC FROZEN
```

### Code Evidence

| File | Line | Issue |
|------|------|-------|
| `sdcard_sdio.c` | 102 | `SD_Init()` called in reset - **BLOCKING** |
| `sdcard_sdio.c` | 272 | `sdcardSdio_reset(); goto doMore;` - infinite loop risk |
| `sdcard_sdio.c` | 332 | Same pattern after write timeout |
| `sdcard_sdio.c` | 360 | Same pattern after read error |
| `sdmmc_sdio_hal.c` | 339 | `HAL_SD_Init(&hsd)` - **BLOCKING HAL call** |
| `sdmmc_sdio_hal.c` | 279 | DMA priority LOW - can be starved |
| `sdmmc_sdio_hal.c` | 297 | SDMMC interrupt priority 2 |
| `fc_core.c` | 894 | `blackboxStart()` at arm triggers the chain |

### Why F765/H743 Specifically

1. These MCUs use SDMMC peripheral (not legacy SDIO)
2. The HAL rewrite specifically targeted F7 and H7
3. Different DMA controllers have different timing characteristics
4. F4 still uses older custom driver (not affected)

---

## HAL Version Analysis

### Current INAV HAL: V1.2.2 (April 2017) - 9 YEARS OLD!

**Latest Available:** V1.3.3 (July 2025)

### Relevant SD/SDMMC Fixes in Newer HAL Versions

| Version | Date | Fix |
|---------|------|-----|
| **V1.3.2** | Apr 2025 | Removed redundant condition from `HAL_SD_InitCard()` |
| **V1.3.2** | Apr 2025 | Added check before aborting DMA in `HAL_MMC_IRQHandler()` |
| **V1.3.2** | Apr 2025 | Updated `SDMMC_DATATIMEOUT` for different clock scenarios |
| **V1.3.0** | Jun 2022 | **Added 2ms power-up wait before SD init sequence** |
| **V1.2.8** | Feb 2020 | **Improved handle state and error management** |

### Key HAL Fixes That May Help

1. **V1.3.0 added 2ms power-up delay** in `HAL_SD_InitCard()` - could prevent initialization race condition
2. **V1.2.8 improved error management** - better state handling could prevent blocking reset loops
3. **V1.3.2 fixed DMA abort handling** - could prevent DMA-related hangs

---

## Proposed Fixes

### Option 1: Update STM32F7 HAL (Recommended)

The `update-stm32f7-hal` project is already queued. Updating from V1.2.2 → V1.3.3 includes fixes for:
- SD card initialization timing
- Error state management
- DMA abort handling

**Action:** Prioritize HAL update and test specifically for arming lockup.

### Option 2: Code-Level Fixes (If HAL Update Insufficient)

1. **Non-blocking reset**: Don't call `HAL_SD_Init()` inline in poll loop
   - Use state machine to schedule init on next cycle

2. **Remove `goto doMore` after reset**:
   - Let next `sdcard_poll()` cycle handle retry
   - Prevents blocking loop

3. **Limit retry attempts**:
   - Add counter to prevent infinite reset loop
   - After N failures, mark SD card as unavailable

4. **Increase DMA priority**:
   - Change from `DMA_PRIORITY_LOW` to `DMA_PRIORITY_MEDIUM`
   - Prevent starvation by other DMA operations

### Option 3: Workaround for Users

Until fixed, users can:
1. Arm before GPS fix acquires
2. Remove SD card if not using blackbox
3. Reduce blackbox logging rate to ≤3%
4. Use faster PWM protocols (Dshot300+)

---

## Success Criteria

- [x] Root cause identified
- [x] Theory validated with code evidence
- [x] HAL version gap identified with relevant fixes
- [ ] Fix proposed or workaround documented
- [ ] Findings reported to upstream
- [ ] HAL update tested for this specific issue

## Files Investigated

**Key Files (Confirmed Issues):**
- `src/main/drivers/sdcard/sdcard_sdio.c` - Blocking reset loop
- `src/main/drivers/sdcard/sdmmc_sdio_hal.c` - HAL wrapper, DMA config
- `src/main/fc/fc_core.c` - Arming triggers blackboxStart()
- `src/main/blackbox/blackbox.c` - blackboxStart() → blackboxDeviceOpen()

**HAL Files:**
- `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/` - V1.2.2 (outdated)

## References

- Issue #11299: https://github.com/iNavFlight/inav/issues/11299
- Issue #10586: https://github.com/iNavFlight/inav/issues/10586
- F7 SDIO HAL commit: `3561feeb9` (Dec 10, 2024)
- STM32F7 HAL Release Notes: https://github.com/STMicroelectronics/stm32f7xx-hal-driver/blob/master/Release_Notes.html
- User CLI diff (10586): https://github.com/user-attachments/files/18388760/diff.txt
- User CLI diff (11299): https://github.com/user-attachments/files/24956264/INAV_9.0.0_cli.txt

## Related Projects

- `update-stm32f7-hal` - HAL update may fix this issue
- `update-stm32f4-hal` - For comparison (F4 not affected)

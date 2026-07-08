# Status Report: F765/H743 Arming Lockup Investigation - Root Cause Identified

**Date:** 2026-02-21 13:29
**From:** Developer
**To:** Manager
**Type:** Status Report
**Re:** F765/H743 Arming Lockup (Issue #11348)

## Investigation Status: COMPLETE

The root cause of the F765/H743 arming lockup has been identified and documented. The issue stems from HAL-based SD card initialization blocking the arming sequence.

---

## Root Cause Analysis

### Primary Issue
Commit 3561feeb9 (December 2024) replaced the custom F7 SDIO driver with a HAL-based implementation. The HAL_SD_Init() function is BLOCKING (up to 100ms per call), creating severe timing issues during arming.

### Blocking Mechanism
The following code pattern creates an infinite blocking loop:
- **sdcard_sdio.c:102** - SD_Init() called in reset (blocking call)
- **sdcard_sdio.c:272** - `sdcardSdio_reset(); goto doMore;` (infinite loop risk)
- The "goto doMore" causes the reset to be called repeatedly without yielding
- Combined with blocking HAL calls, this prevents the scheduler from running

### Code Evidence

**sdmmc_sdio_hal.c:339** - The actual blocking call:
```c
HAL_SD_Init()  // Blocks up to 100ms
```

**sdmmc_sdio_hal.c:279** - DMA Priority Configuration:
```c
DMA priority = LOW  // Can be starved by higher-priority peripherals
```

**fc_core.c:894** - Trigger Point:
```c
blackboxStart()  // Called at arm - initiates SD card chain
```

### Additional Finding: HAL Version Gap
The current STM32F7 HAL is severely outdated:
- **Current:** V1.2.2 (April 2017) - **9 YEARS OLD**
- **Latest:** V1.3.3 (July 2025)
- **Relevant improvements in V1.3.0+:**
  - Fixed SD card initialization timing
  - Improved error state handling
  - Better SDIO DMA configuration
  - Timeout handling improvements

---

## Impact Assessment

**Affected Boards:**
- STM32F765 (confirmed)
- STM32H743 (suspected - same code path)

**Trigger Condition:**
Arming with SD card logging enabled (Blackbox feature)

**Severity:** HIGH
- Prevents flight operations on affected boards
- Affects users with SD card logging/telemetry features
- Workaround: Disable Blackbox logging

---

## Recommended Action

### Priority 1: Verify HAL Update Project
The `update-stm32f7-hal` project should be prioritized. A HAL update to V1.3.0+ may directly resolve this issue without additional code changes. The new HAL version includes specific fixes for SD card initialization timing and error state handling.

### Alternative Fixes (if HAL update insufficient)

1. **Make sdcardSdio_reset() non-blocking**
   - Implement state machine approach
   - Break blocking HAL call into smaller steps
   - Allow scheduler to run between steps

2. **Remove "goto doMore" after reset**
   - Let next poll cycle handle retry
   - Reduces risk of infinite loops
   - Better integration with scheduler

3. **Add retry counter**
   - Prevent infinite reset loops
   - Log excessive reset attempts
   - Gracefully degrade if SD card fails

4. **Increase DMA Priority**
   - Change SD DMA from LOW to MEDIUM
   - Reduces DMA starvation risk
   - May improve initialization reliability

---

## Investigation Files

All detailed findings, code analysis, and technical documentation are preserved in:
`claude/projects/active/investigate-f765-arming-lockup/`

---

## Next Steps

1. ✅ Investigation complete and findings documented
2. ⏳ Awaiting decision on HAL update prioritization
3. ⏳ If HAL update approved, verify it resolves the issue
4. ⏳ If additional fixes needed, implement alternatives in order above

---

**Developer**

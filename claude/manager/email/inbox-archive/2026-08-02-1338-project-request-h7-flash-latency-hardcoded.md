# Project Request: FLASH_LATENCY_2 hardcoded regardless of STM32H7 silicon revision

**Date:** 2026-08-02 13:38
**From:** Developer
**To:** Manager
**Type:** Project Request
**Repository:** inav
**File:** src/main/target/system_stm32h7xx.c

## Problem

While reviewing PR iNavFlight/inav#11756 (new Synerduino H743/F405 targets, which set `HSE_MHZ 25` and would fail to build due to a separate PLL2 issue — see below), I traced through `SystemClockHSE_Config()` in `src/main/target/system_stm32h7xx.c` and found the flash wait-state configuration doesn't vary by silicon revision, even though the code's own comment says it should.

`system_stm32h7xx.c:359`:

```c
if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
```

`FLASH_LATENCY_2` is passed unconditionally for both RevY and RevV silicon. But the comment directly above it (lines 353-357) says:

```c
// For HCLK=200MHz with VOS1 range, ST recommended flash latency is 2WS.
// RM0433 (Rev.5) Table 12. FLASH recommended number of wait states and programming delay
//
// For higher HCLK frequency, VOS0 is available on RevV silicons, with FLASH wait states 4WS
// AN5312 (Rev.1) Section 1.2.1 Voltage scaling Table.1
```

RevV runs PLL1 at N=480 (`pll1ConfigRevV`, line 221-229) → SYSCLK=480MHz nominal → HCLK=240MHz (fixed /2 divider, line 347), at VOS0. Per the comment's own citation, that should use 4WS, but the code never branches on revision to apply it — it's 2WS for RevY and RevV alike.

Insufficient flash wait states relative to actual HCLK can cause the flash controller to return corrupted/stale data on reads, manifesting as sporadic hard faults or instruction/data corruption, often intermittent and worse under thermal/voltage stress. This looks like a pre-existing gap independent of any specific target or the PR #11756 investigation that surfaced it.

## Related context (found in the same investigation, not required reading to act on this one)

Separately, PR #11756's new H743 targets set `HSE_MHZ 25` with `USE_SDCARD_SDIO` enabled, which trips a `STATIC_ASSERT` in the same file (line 506, PLL2 config) because 25MHz isn't a multiple of 1.6MHz — that PR won't compile as-is. Even setting that aside, the PLL1 M-divider formula (line 259) assumes HSE is a clean even number of MHz to land VCI at exactly 2MHz; 25MHz doesn't divide evenly, so PLL1/SYSCLK drifts a few percent above nominal (RevV: 500MHz vs 480MHz nominal) as an unintended side effect of integer truncation. If it's useful, this could be scoped as a related project, but the FLASH_LATENCY_2 gap stands on its own regardless of HSE frequency.

## Suggested next step

Confirm against RM0433 Table 12 / AN5312 Table 1 what wait-state count each VOS/HCLK combination actually requires, then make `FLASH_LATENCY_2`/`_4` conditional on which `pll1Config` (RevY vs RevV) was selected in `SystemClockHSE_Config()`.

---
**Developer**

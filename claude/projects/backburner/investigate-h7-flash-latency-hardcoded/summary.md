# Project: Investigate H7 FLASH_LATENCY_2 Hardcoded Regardless of Silicon Revision

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-08-03
**Estimated Time:** 2-5 hours

## Overview

`SystemClockHSE_Config()` in `src/main/target/system_stm32h7xx.c` passes
`FLASH_LATENCY_2` unconditionally to `HAL_RCC_ClockConfig()`
(`system_stm32h7xx.c:359`), regardless of which silicon revision/PLL1 config
was selected. The comment directly above it (lines 353-357) says RevV
silicon at VOS0 (HCLK=240MHz) needs 4WS, but the code never branches on
revision to apply it.

## Problem

Insufficient flash wait states relative to actual HCLK can cause the flash
controller to return corrupted/stale data on reads — sporadic hard faults or
instruction/data corruption, often intermittent and worse under thermal/
voltage stress. RevV runs PLL1 at N=480 (`pll1ConfigRevV`, line 221-229) →
SYSCLK=480MHz nominal → HCLK=240MHz (fixed /2 divider, line 347) at VOS0. Per
the comment's own citations (RM0433 Table 12, AN5312 Table 1), that
combination should use 4WS, but gets 2WS like RevY does.

Flagged by developer 2026-08-02 while investigating an unrelated PR
(#11756, new Synerduino H743/F405 targets) that doesn't compile due to a
separate PLL2/HSE_MHZ issue in the same file — see Related below.

## Objectives

1. Confirm against RM0433 (Rev.5) Table 12 and AN5312 (Rev.1) Section 1.2.1
   Table 1 exactly which flash wait-state count each VOS/HCLK combination
   requires (RevY and RevV, all HCLK values INAV actually configures).
2. Determine whether `FLASH_LATENCY_2` should become conditional on which
   `pll1Config` (RevY vs RevV) was selected in `SystemClockHSE_Config()`, and
   implement the fix.
3. Assess real-world exposure: which shipped H7 targets run RevV silicon at
   VOS0/240MHz today, and whether this explains any known-but-unexplained
   intermittent hard-fault reports.

## Scope

**In Scope:**
- `src/main/target/system_stm32h7xx.c` flash latency configuration
- Datasheet/reference manual verification (RM0433, AN5312)
- Testing across affected H7 targets

**Out of Scope:**
- PR #11756's separate PLL2/HSE_MHZ STATIC_ASSERT failure and PLL1 M-divider
  rounding drift for non-even HSE frequencies (same file, same investigation,
  but an independent issue — see Related Work below; not blocking this one)

## Related Work

PR iNavFlight/inav#11756 (new Synerduino H743/F405 targets) surfaced this
while setting `HSE_MHZ 25`, which separately trips a `STATIC_ASSERT` in the
same file (line 506, PLL2 config) because 25MHz isn't a multiple of 1.6MHz,
and causes PLL1/SYSCLK to drift a few percent above nominal due to integer
M-divider truncation. That issue stands independently of this one and can be
scoped as a follow-up project if needed — not created yet, ask developer if
they want it opened once this is underway.

## Success Criteria

- [ ] Wait-state requirement per RevY/RevV × VOS/HCLK combination confirmed
      against RM0433/AN5312
- [ ] Fix implemented and builds clean across the H7 target matrix
- [ ] Hardware-verified on at least one RevV H7 board at 240MHz/VOS0
- [ ] PR opened against the correct base branch

## Estimated Time
2-5 hours (mostly datasheet verification + hardware test time)

## Priority Justification

HIGH: this is silent data/instruction corruption risk on H7 RevV boards at
VOS0, not a feature gap — the failure mode (intermittent hard faults) is
exactly the kind of hard-to-diagnose field issue that erodes trust in the
firmware. Not CRITICAL only because it's apparently gone unnoticed in
practice so far (or been misattributed to other causes), so no emergency
out-of-band fix is required.

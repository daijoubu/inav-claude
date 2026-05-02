# Project: test-pr-11390-dshot-dma

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM-HIGH
**Type:** Testing
**Created:** 2026-05-02
**Estimated Effort:** 2–3 hours (bench time)

## Overview

Before/after bench test of PR #11390, which fixes intermittent F7/H7 lockups at DShot DMA startup by waiting for the DMA EN bit to clear before reconfiguring registers.

## Problem

STM32F7/H7 DShot DMA reconfiguration could silently corrupt data if the DMA stream EN bit hadn't cleared after `LL_DMA_DisableStream()`. This caused intermittent lockups on F765 boards (observed on MATEKF765SE in Swordfish airframe).

## Solution (in PR)

Adds a bounded spin-wait (10,000 iterations with `__NOP()`) after `LL_DMA_DisableStream()`. If EN bit fails to clear, reconfiguration is skipped entirely to avoid writing stale values. Prevents the race condition in `impl_timerPWMPrepareDMA()`.

## Test Approach

- **Before:** Flash unmodified current firmware, run arming + DShot logging test
- **After:** Flash PR #11390 build, run identical test
- **Key requirement:** At least 1 DShot motor on each timer to maximise DMA contention

Pre-built firmware available at:
https://github.com/iNavFlight/pr-test-builds/releases/tag/pr-11390

## Success Criteria

- [ ] Unmodified firmware baseline run completed with no lockup (or lockup documented)
- [ ] PR #11390 firmware run completed with no lockup
- [ ] Arming/disarming cycles stable on both builds
- [ ] Blackbox logs captured for both runs
- [ ] Results posted as comment on PR #11390

## Related

- **PR:** [#11390](https://github.com/iNavFlight/inav/pull/11390)
- **Author:** sensei-hacker
- **Hardware:** MATEKF765SE (STM32F765)
- **Assignment:** `manager/email/sent/2026-05-02-task-test-pr-11390-dshot-dma.md`

# Request: Add LOG_DEBUG Cleanup to feature-stm32f7-can-tx-isr

**Date:** 2026-05-02 09:30
**From:** Developer
**To:** Manager
**Re:** feature-stm32f7-can-tx-isr

## Request

While investigating ITCM headroom, I audited the DroneCAN F7 driver for active debug logging. Please add a cleanup sub-task to `feature-stm32f7-can-tx-isr` (or as a prerequisite commit in that branch) to address the following before the PR goes upstream:

## What Needs Cleaning Up

**Hard requirement (blocking for ISR work):**
- Remove or guard `LOG_DEBUG` from `canardSTM32Transmit()` line 166 — once TX moves to ISR context, calling printf-family functions from an ISR is undefined behaviour. Must be replaced with a counter/flag that is logged outside interrupt context.

**Style/quality (should fix in same PR):**
- `canardSTM32ComputeTimings()` has 6 active `LOG_DEBUG` calls — acceptable since it only runs at init, but verbose. Consider reducing to one summary line.
- `dronecan.c` transfer handler has ~10 `LOG_DEBUG` calls that fire on every received frame — these should be gated or reduced before upstream submission.

## Background

`USE_LOG` has been unconditionally defined in `common.h` since February 2019 (commit 45553a06b) — it is intentional and permanent, not an accidentally-left-in flag. The logging system is runtime-filtered, so these calls compile into all production builds. The issue is logging discipline in hot paths and the hard constraint against any logging inside ISR context.

---
**Developer**

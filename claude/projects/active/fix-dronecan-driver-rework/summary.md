# Project: DroneCAN CAN Driver Rework — TX Priority and ISR Architecture

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix
**Created:** 2026-06-11
**Estimated Time:** 7–10 hours (Phases 1+2) + ~1 hr/project for Phase 3

## Overview

Fix two confirmed bugs in the H743 FDCAN driver and one design defect in the F765 bxCAN TX path, then rebase all pending DroneCAN branches onto the corrected base. Introduces a sound ISR-driven architecture: libcanard as authoritative priority queue, shallow hardware staging buffer, ISR-driven refills.

## Problem

DroneCAN TX path has confirmed priority inversion issues:
1. **H743 FDCAN:** Configured in TX FIFO mode (insertion order) rather than TX Queue mode (priority order). Queue depth 32 stages too many frames, defeating libcanard's priority scheduler.
2. **F765 bxCAN (PR #11560):** Software TX queue is a plain FIFO — frames arriving between poll cycles will queue in insertion order, causing priority inversion under ESC/servo load.
3. **libcanard call sites:** Not ISR-safe. NVIC-level masking needed around all `canardBroadcast` / `canardRequestOrRespond` / `canardCleanupStaleTransfers` call sites.

## Objectives

1. Fix H743: FDCAN Queue mode + depth 3
2. Fix H743: Add TX-complete ISR pump
3. Fix dronecan.c: NVIC masking at all libcanard call sites
4. Fix F765: Replace SW FIFO queue with ISR-driven depth-1 pattern
5. Rebase all pending DroneCAN projects onto clean base
6. (Phase 4, post-merge) HITL validation under simulated bus load

## Scope

**In Scope:**
- `inav/src/main/drivers/canard_stm32h7xx_driver.c` — Queue mode + depth + ISR
- `inav/src/main/drivers/canard_stm32f7xx_driver.c` — remove SW queue, add ISR depth-1
- `inav/src/main/flight/dronecan.c` — NVIC masking at all call sites
- All active DroneCAN branches: rebase + add NVIC masking to any new call sites

**Out of Scope:**
- `CanDriver_t` hardware abstraction vtable (future project when second CAN protocol added)
- F4 / AT32 targets (bxCAN, no priority queue concern at same level)
- RX path

## Implementation Plan

### Phase 1: H7 fixes + ISR architecture (3–4 hrs)
Branch: `fix/dronecan-h7-tx-priority-isr` off `maintenance-10.x`

1. `canard_stm32h7xx_driver.c:181` — `FDCAN_TX_FIFO_OPERATION` → `FDCAN_TX_QUEUE_OPERATION`
2. `canard_stm32h7xx_driver.c:178` — `TxFifoQueueElmtsNbr = 32` → `3`
3. `canard_stm32h7xx_driver.c` — Add `HAL_FDCAN_TxBufferCompleteCallback` ISR pump; enable `FDCAN_IT_TX_COMPLETE`
4. `dronecan.c` — Wrap all `canardBroadcast` / `canardRequestOrRespond` / `canardCleanupStaleTransfers` with `NVIC_DisableIRQ` / `NVIC_EnableIRQ`

Build matrix: F4, F7, H7, AT32, SITL — all must pass.

### Phase 2: F7 driver rework (2–3 hrs)
Branch: rebase/new PR replacing #11560, built on Phase 1

1. `canard_stm32f7xx_driver.c` — Remove `canTxQueue`, `canTxDrainQueue()`, `TX_QUEUE_SIZE`
2. `canard_stm32f7xx_driver.c` — `TransmitFifoPriority = ENABLE` → `DISABLE`
3. `canard_stm32f7xx_driver.c` — `canardSTM32Transmit()`: direct HW mailbox attempt, return 0 if full
4. `canard_stm32f7xx_driver.c` — ISR callbacks: NVIC mask → peek libcanard → load 1 frame → pop → unmask

### Phase 3: Rebase all pending DroneCAN projects (~1 hr each)
Projects to rebase (in dependency order):
- `fix/dronecan-gps-health-guard` (review-dronecan-gps-node-health)
- `feature/dronecan-getnodeinfo`
- `feature/dronecan-param-getset`
- `feature/dronecan-dna-server` + `feature/dronecan-dna-configurator`
- `feature/dronecan-magnetometer` (check for new canardBroadcast call sites)
- `feature/canbus-errors-blackbox` (branch off updated maintenance-10.x after Phase 2 merges)

Any project that adds `canardBroadcast()` or `canardRequestOrRespond()` call sites must wrap with NVIC masking.

### Phase 4: HITL validation (post-Phase 2, separate project)
Use HITL hybrid simulation to stress-test under simulated ESC/servo bus load. Validate interrupt priority configuration and confirm no scheduler starvation or priority inversion under load. Activated as separate project after Phase 2 lands.

## Success Criteria

- [ ] Phase 1: H743 in Queue mode, depth 3, ISR-driven, builds clean on all targets
- [ ] Phase 2: F765 at depth 1, ISR-driven, no SW queue, builds clean on all targets
- [ ] Phase 2: PR #11560 superseded (converted to draft or closed, replaced by Phase 2 PR)
- [ ] Phase 3: All DroneCAN branches rebased, NVIC masking added at new call sites
- [ ] Phase 1 + 2 PRs submitted to maintenance-10.x
- [ ] No priority inversion under any load scenario

## Estimated Time

- Phase 1: 3–4 hours
- Phase 2: 2–3 hours
- Phase 3: ~1 hour per branch (6–7 branches)
- Phase 4: TBD (separate project)

## Priority Justification

All pending DroneCAN features will share this TX path. Priority inversion under ESC/servo load is a flight-safety concern. Fixing before any further feature PRs land is significantly cheaper than debugging in production.

## Notes

- PR #11560 converted to **draft** (2026-06-11) with comment explaining the SW queue ordering defect. ISR architecture and TXFP=ENABLE from #11560 are correct and will be preserved in Phase 2.
- `feature-dronecan-magnetometer` should hold new `canardBroadcast()` additions until Phase 1 lands.
- `feature-canbus-errors-blackbox` remains blocked on Phase 2 completing (replaces dependency on #11560).

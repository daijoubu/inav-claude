# Todo List: DroneCAN CAN Driver Rework

## Phase 1: H7 Driver Fixes + ISR Architecture

Branch: `fix/dronecan-h7-tx-priority-isr` off `maintenance-10.x`

- [ ] Change `FDCAN_TX_FIFO_OPERATION` → `FDCAN_TX_QUEUE_OPERATION` (canard_stm32h7xx_driver.c:181)
- [ ] Change `TxFifoQueueElmtsNbr = 32` → `3` (canard_stm32h7xx_driver.c:178)
- [ ] Add `HAL_FDCAN_TxBufferCompleteCallback` ISR pump
- [ ] Enable `FDCAN_IT_TX_COMPLETE` in H7 driver init
- [ ] Wrap all `canardBroadcast()` call sites in dronecan.c with NVIC_DisableIRQ / NVIC_EnableIRQ
- [ ] Wrap all `canardRequestOrRespond()` call sites with NVIC masking
- [ ] Wrap `canardCleanupStaleTransfers()` call sites with NVIC masking
- [ ] Build matrix: F4, F7, H7, AT32, SITL — all must pass
- [ ] Submit Phase 1 draft PR to maintenance-10.x

## Phase 2: F7 Driver Rework (replaces PR #11560)

Branch: new PR off Phase 1 base

- [ ] Remove `canTxQueue`, `canTxDrainQueue()`, `TX_QUEUE_SIZE` from canard_stm32f7xx_driver.c
- [ ] Change `TransmitFifoPriority = ENABLE` → `DISABLE`
- [ ] Rework `canardSTM32Transmit()` to attempt direct HW mailbox, return 0 if full
- [ ] Add ISR callbacks: NVIC mask → peek libcanard → load 1 frame → pop → unmask
- [ ] Build matrix: all targets pass
- [ ] Post review comment on PR #11560 documenting ordering issue and replacement plan
- [ ] Submit Phase 2 draft PR to maintenance-10.x

## Phase 3: Rebase All Pending DroneCAN Projects

Rebase onto `fix/h7-dronecan-driver` (Phase 2 branch, PR #11607) in dependency order.
Actual stack (confirmed via git merge-base): getnodeinfo → param-getset → {gps-health-guard, dna-server}

- [x] Rebase `feature/dronecan-getnodeinfo` onto `fix/h7-dronecan-driver` — check for new canardBroadcast/request call sites needing NVIC masking
- [x] Rebase `feature/dronecan-param-getset` onto rebased `feature/dronecan-getnodeinfo` — check for new call sites
- [x] Rebase `fix/dronecan-gps-health-guard` onto rebased `feature/dronecan-param-getset` — check for new call sites
- [x] Rebase `feature/dronecan-dna-server` onto rebased `feature/dronecan-param-getset` — check for new call sites
- [x] Rebase `feature/dronecan-dna-configurator` (configurator side) — already based on `maintenance-10.x`, nothing to rebase until upstream advances
- [ ] Rebase `feature/dronecan-magnetometer` (once created) — wrap any new call sites — **blocked: branch not yet created, project still TODO**
- [ ] Branch `feature/canbus-errors-blackbox` off `fix/h7-dronecan-driver` and begin implementation — **blocked: branch not yet created; project's PLAN.md missing from working tree, needs manager follow-up**
- [x] Verify each rebased branch builds clean on full matrix

## Completion

- [ ] Phase 1 PR reviewed and merged to maintenance-10.x — PR #11607 open, CI green
- [ ] Phase 2 PR reviewed and merged to maintenance-10.x
- [x] PR #11560 converted to draft (or closed/replaced) — done 2026-06-11
- [x] All DroneCAN branches rebased and verified (getnodeinfo, param-getset, gps-health-guard, dna-server, dna-configurator)
- [ ] Update Merge Watch table in INDEX.md to reflect new PR chain — manager task
- [x] Send completion report to manager

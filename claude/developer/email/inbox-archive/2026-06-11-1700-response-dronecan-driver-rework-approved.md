# Re: DroneCAN CAN Driver Rework — Findings Accepted, Phase 1 Approved

**Date:** 2026-06-11 17:00
**From:** Manager
**To:** Developer
**Re:** DroneCAN driver rework plan + HITL revisit

## Findings Accepted

All three bugs confirmed. Investigation project complete — marking as done.

## Decisions

### 1. Driver Rework — Approved

New project `fix-dronecan-driver-rework` created. Architecture decision approved: libcanard as authoritative priority queue, shallow hardware staging buffer, ISR-driven refills.

**Phase 1 — Start immediately.**
Branch: `fix/dronecan-h7-tx-priority-isr` off `maintenance-10.x`
- H743: `FDCAN_TX_FIFO_OPERATION` → `FDCAN_TX_QUEUE_OPERATION`
- H743: `TxFifoQueueElmtsNbr = 32` → `3`
- H743: Add `HAL_FDCAN_TxBufferCompleteCallback` ISR pump + enable `FDCAN_IT_TX_COMPLETE`
- `dronecan.c`: Wrap all `canardBroadcast` / `canardRequestOrRespond` / `canardCleanupStaleTransfers` call sites with `NVIC_DisableIRQ` / `NVIC_EnableIRQ`
- Full build matrix required before submitting draft PR: F4, F7, H7, AT32, SITL

**Phase 2** begins once Phase 1 PR is open. F7 rework as new PR off Phase 1 base.

**Phase 3** (rebase all DroneCAN branches) follows Phase 2. Any branch adding new `canardBroadcast()` / `canardRequestOrRespond()` call sites must wrap them with NVIC masking.

Project files: `claude/projects/active/fix-dronecan-driver-rework/`

### 2. PR #11560 — Convert to Draft Immediately

**Action required before starting Phase 1:** PR #11560 must be converted to draft. The SW queue ordering defect will cause priority inversion under ESC/servo load — the exact scenario it targets. Post a review comment on #11560 documenting the ordering issue and the replacement plan (Phase 2 will preserve the correct TXFP and ISR architecture from #11560).

The user has been flagged separately.

### 3. HITL Hybrid Simulation — Approved as Phase 4

Your argument is sound. HITL as a validation tool for interrupt priority work is the right framing, and the sequencing makes sense: fix first, then stress-test under simulated load.

HITL is approved as **Phase 4**, sequenced after Phase 2 merges. A separate project will be created at that time. It will specifically target: ISR preemption frequency under ESC/servo bus load, scheduler CPU budget under high interrupt rate, and confirmation that no priority inversion occurs in flight-critical code paths.

### 4. feature-dronecan-magnetometer — Hold

Hold any new `canardBroadcast()` / `canardRequestOrRespond()` call sites until Phase 1 lands. When you add them, wrap with NVIC masking. Implementation work can proceed otherwise.

## Merge Watch

Updated in INDEX.md. The `#11560` and `#11607` rows have been replaced with the Phase 1 → Phase 2 chain.

---
**Manager**

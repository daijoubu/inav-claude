# DroneCAN CAN Driver Rework — Investigation Findings and Proposed Plan

**Date:** 2026-06-11 15:00
**From:** Developer
**To:** Manager
**Re:** investigate-dronecan-tx-priority-queue — findings, plan, and project impacts

---

## Executive Summary

The DroneCAN TX path has two confirmed bugs on H743 and a design defect on the F765
driver in PR #11560. Investigation also surfaced a sound architectural direction: treat
libcanard as the authoritative priority queue, use a shallow hardware staging buffer,
and drive refills from a TX-complete ISR. This pattern resolves all identified issues,
gives correct behaviour under ESC/servo load, and sets up a clean hardware abstraction
for future protocol stacks (CANaero etc.).

**Recommended immediate action:** Put PR #11560 into draft to prevent merge. Pull the
H7 fixes and ISR architecture work into a new branch and use that as the common base
for all pending DroneCAN work.

---

## Part 1 — Findings

### 1.1 STM32H743 FDCAN Driver (`canard_stm32h7xx_driver.c`)

**Bug 1 — HIGH: TX FIFO mode instead of Queue mode**

`hfdcan1.Init.TxFifoQueueMode = FDCAN_TX_FIFO_OPERATION` (line 181).

In FIFO mode the hardware transmits in insertion order, ignoring CAN arbitration ID
priority. When more than one frame is staged, lower-priority frames already in the FIFO
will be sent before a newly arrived higher-priority frame. For DroneCAN,
`FDCAN_TX_QUEUE_OPERATION` is the correct setting: the hardware selects the pending
frame with the lowest CAN ID (highest DroneCAN priority) before placing it on the bus.
For same-CAN-ID frames (frames within a multi-frame transfer), FDCAN Queue mode uses
the PUT index as a tiebreak, preserving insertion order — so intra-transfer frame
sequencing is also correct.

**Bug 2 — MEDIUM: TX queue depth is 32**

`hfdcan1.Init.TxFifoQueueElmtsNbr = 32` (line 178).

`processCanardTxQueue()` drains the libcanard TX queue until hardware is full. With
depth 32, up to 32 frames are staged in hardware simultaneously. A newly enqueued
high-priority frame enters libcanard but finds no hardware slot and must wait for all
32 staged frames to transmit first, defeating libcanard's priority scheduling. Correct
depth is 3.

**Gap — LOW: No TX-complete ISR pump**

`processCanardTxQueue()` is polled at 500 Hz (2 ms period). With depth reduced to 3,
the queue drains in ~390 µs at 1 Mbit/s. Without an ISR refill the bus idles for up to
~1.6 ms per poll cycle. Negligible at current traffic levels; significant at ESC/servo
bandwidth.

### 1.2 STM32F765 bxCAN Driver — PR #11560 (`feature/stm32f7-can-tx-isr`)

**Bug 3 — MEDIUM: Software TX queue is insertion-ordered (FIFO)**

`canTxQueuePush()` is a plain circular FIFO with no CAN ID ordering. Frames pushed by
`processCanardTxQueue()` are in libcanard priority order at the moment of the call, but
any higher-priority frame that enters libcanard between `dronecanUpdate()` calls is
appended to the back of the software queue behind already-queued lower-priority frames.
Priority inversion. This will manifest under ESC/servo load.

**`TransmitFifoPriority = ENABLE` — correctly chosen, not a bug**

This was initially flagged in the audit but confirmed correct by the user based on
real-world testing. With `TXFP = DISABLE`, bxCAN arbitrates among loaded mailboxes by
mailbox number when CAN IDs are equal (all frames of a multi-frame transfer share a CAN
ID). If mailboxes are not assigned in strict sequence the hardware can transmit frame
N+2 before frame N+1, corrupting the transfer. `TXFP = ENABLE` preserves load order.
This was observed in testing and the setting must be retained in any approach that
loads multiple frames into hardware simultaneously.

**What is correct in PR #11560:** TX-complete ISR callbacks are implemented (correct
pump-from-ISR architecture), ATOMIC_BLOCK seed logic is sound, diagnostics are useful.

### 1.3 libcanard ISR Safety

Neither UAVCAN v0 libcanard nor OpenCyphal v1/v2 libcanard is ISR-safe (both
explicitly state "not thread-safe"). The correct mechanism on Cortex-M is NVIC-level
interrupt masking of the CAN TX IRQ specifically — not BASEPRI, which would also mask
unrelated lower-priority ISRs. This requires no changes to libcanard source files; only
`dronecan.c` call sites and driver ISR callbacks are touched.

---

## Part 2 — Architecture Decision

**Principle:** libcanard is the authoritative priority queue. Hardware is a shallow
staging buffer only. The ISR keeps the staging buffer topped up from libcanard.

```
Application
  │  canardBroadcast() / request / respond
  │  [NVIC_DisableIRQ / EnableIRQ around each call]
  ▼
libcanard TX queue — priority-sorted, insertion-order preserved within same CAN ID
  │  TX-complete ISR: peek → stage to HW → pop
  ▼
HW staging  (3 slots H7 / 1 slot F7)
  │
  ▼
CAN bus arbitration
```

**H743 FDCAN — ISR-driven, depth 3:**
`FDCAN_TX_QUEUE_OPERATION`, `TxFifoQueueElmtsNbr = 3`, `FDCAN_IT_TX_COMPLETE` enabled,
`HAL_FDCAN_TxBufferCompleteCallback` refills from libcanard. Depth 3 is safe: FDCAN
Queue mode resolves same-CAN-ID ties by PUT index (insertion order).

**F765 bxCAN — ISR-driven, depth 1:**
Remove `canTxQueue` and `canTxDrainQueue()`. `TXFP = DISABLE` — safe at depth 1 since
only 1 frame is ever in hardware (mailbox tiebreak issue cannot occur). ISR callbacks
load exactly 1 frame per completion. Throughput cost is negligible (~200 ns ISR
overhead vs 3 µs minimum inter-frame gap).

---

## Part 3 — Future: Shared Hardware Abstraction (`CanDriver_t`)

With both drivers on the same ISR-driven pattern they share an implicit interface.
The natural next step is a `CanDriver_t` vtable decoupling hardware from protocol
stack, enabling CANaero or any future protocol to use the same drivers without
modification. `CanFrame_t` can be binary-compatible with `CanardCANFrame` for
zero-copy. Recommended trigger: when a second CAN protocol is actively being added.
This is a follow-on project, not a prerequisite for the fixes.

---

## Part 4 — Proposed Plan

### Phase 1: H7 driver fixes + ISR architecture (new branch off master)

Branch: `fix/dronecan-h7-tx-priority-isr`

| # | File | Change |
|---|------|--------|
| 1 | `canard_stm32h7xx_driver.c:181` | `FDCAN_TX_FIFO_OPERATION` → `FDCAN_TX_QUEUE_OPERATION` |
| 2 | `canard_stm32h7xx_driver.c:178` | `TxFifoQueueElmtsNbr = 32` → `3` |
| 3 | `canard_stm32h7xx_driver.c` | Add `HAL_FDCAN_TxBufferCompleteCallback` ISR pump; enable `FDCAN_IT_TX_COMPLETE` |
| 4 | `dronecan.c` | Wrap all `canardBroadcast` / `canardRequestOrRespond` / `canardCleanupStaleTransfers` call sites with `NVIC_DisableIRQ` / `NVIC_EnableIRQ` |

Build matrix: F4, F7, H7, AT32, SITL — all must pass.

### Phase 2: F7 driver rework (rework of PR #11560 onto Phase 1 base)

| # | File | Change |
|---|------|--------|
| 5 | `canard_stm32f7xx_driver.c` | Remove `canTxQueue`, `canTxDrainQueue()`, `TX_QUEUE_SIZE` |
| 6 | `canard_stm32f7xx_driver.c` | `TransmitFifoPriority = ENABLE` → `DISABLE` |
| 7 | `canard_stm32f7xx_driver.c` | `canardSTM32Transmit()`: direct HW mailbox attempt, return 0 if full |
| 8 | `canard_stm32f7xx_driver.c` | ISR callbacks: NVIC mask → peek libcanard → load 1 frame → pop → unmask |

`dronecan.c` NVIC masking from Phase 1 covers F7 as well — no further changes needed.

### Phase 3: Rebase all pending DroneCAN projects

All active DroneCAN work must be rebased onto the Phase 1+2 base. Any project that
adds `canardBroadcast()` or `canardRequestOrRespond()` call sites must wrap them with
`NVIC_DisableIRQ` / `NVIC_EnableIRQ`. Manager should audit all active DroneCAN projects
for this dependency and coordinate rebase order.

---

## Part 5 — PR #11560 Recommendation

**Action: Put PR #11560 into draft immediately.**

The software TX queue ordering defect means the PR will cause priority inversion under
ESC/servo load — the exact use case it is preparing for. The ISR architecture and TXFP
decision are correct and will be preserved in the Phase 2 rework. The PR author should
be informed via a review comment documenting the ordering issue and the plan.

---

## Part 6 — Impact on Pending DroneCAN Projects

**feature-dronecan-magnetometer (ACTIVE):** Directly impacted. Any `canardBroadcast()`
or `canardRequestOrRespond()` calls added by this project must be wrapped with NVIC
masking. Recommend holding or branching to expect a rebase onto Phase 1.

All other active DroneCAN projects should be audited. Projects not touching
`dronecan.c` or the CAN driver files are unaffected.

---

## Effort Estimate

| Phase | Estimate |
|-------|----------|
| Phase 1 — H7 fixes + ISR + dronecan.c masking | 3–4 hours |
| Phase 2 — F7 rework | 2–3 hours |
| Phase 3 — Rebase per DroneCAN project | ~1 hour per project |

---
**Developer**

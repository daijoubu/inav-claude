# Task Assignment: Investigate DroneCAN TX Priority — FIFO vs Queue and Queue Depth

**Date:** 2026-06-11 12:00
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-tx-priority-queue
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3–5 hours

## Task

Audit the DroneCAN TX path on STM32H743 (FDCAN hardware) and STM32F765 (bxCAN with software queue from PR #11560) for priority inversion risk. Produce written findings and fix any issues found.

## Background

DroneCAN encodes transfer priority in the CAN arbitration ID. Bus arbitration enforces priority between nodes, but **within a single node**, the TX queue must also dispatch frames in priority order (by CAN ID), not insertion order. If it doesn't, a newly arrived high-priority frame can be blocked behind older low-priority frames already staged in hardware — priority inversion.

Two specific concerns have been raised:

**1. STM32H743 FDCAN hardware TX mode**

The STM32H7 FDCAN peripheral can operate in either TX FIFO mode or TX Queue mode (selected by the TFQM bit / `TxFifoQueueMode` HAL init field):
- **FIFO mode** — sends in insertion order; ignores CAN ID priority
- **Queue mode (`FDCAN_TX_QUEUE_OPERATION`)** — selects the pending frame with the smallest CAN ID (highest arbitration priority) when multiple frames are staged

For DroneCAN, **Queue mode is the correct choice**. If INAV's H743 FDCAN driver is using FIFO mode, priority inversion is possible whenever more than one frame is staged in hardware.

**2. Hardware queue depth**

Even in Queue mode, the hardware should not be stuffed with many frames at once. CAN arbitration only happens before a frame starts — once a frame is on the bus it cannot be preempted mid-frame. If you preload 3 low-priority frames into hardware, a newly arrived urgent frame must wait for all of them. Best practice:
- Keep the hardware queue at **1 frame** (safest) or **2 frames** (workable if validated)
- Let **libcanard's TX queue** be the master scheduler — it is already priority-sorted
- Use a **pump_tx() pattern**: push one frame from libcanard into hardware after each enqueue and after each TX-complete ISR callback

**3. F765 bxCAN software queue (PR #11560)**

The `feature/stm32f7-can-tx-isr` branch introduces a software TX queue for the F765 bxCAN driver. The same question applies: is this SW queue ordered by CAN ID, or by insertion? What is its depth? Does it use a pump pattern?

## What to Do

### Phase 1: Audit

1. **Locate the H743 FDCAN driver** — find `TxFifoQueueMode` configuration
   - Is it `FDCAN_TX_FIFO_OPERATION` or `FDCAN_TX_QUEUE_OPERATION`?
   - How many frames are staged into hardware at once?

2. **Find the pump_tx() equivalent** in the H743 driver (may be inlined)
   - Is it called after a libcanard frame is enqueued?
   - Is it called from the TX-complete ISR or callback?

3. **Check out PR #11560** (`feature/stm32f7-can-tx-isr`) and audit the F765 SW queue
   - Is the queue ordered by CAN ID or insertion order?
   - What is the depth?
   - Does it use a pump pattern?

4. **Verify libcanard TX API names** in INAV's vendored libcanard headers
   - Confirm the actual function names for peek/pop from the TX queue
   - Note: guidance references `canardPeekTxQueue()` / `canardPopTxQueue()` — verify these are correct for the version INAV uses

### Phase 2: Fix / Recommend

- If H743 is using FIFO mode → change to `FDCAN_TX_QUEUE_OPERATION`
- If H743 hardware depth > 2 → reduce and document rationale
- If pump_tx() call sites are missing → add them
- If F765 SW queue in #11560 is insertion-ordered → file a note on the PR or propose a fix
- Document findings (brief inline comments or a findings note in the project directory)

### Phase 3: Verify

- Any code changes must build clean: F4, F7, H7, AT32, SITL
- No regressions in existing CAN/DroneCAN behaviour

## Copilot Guidance (pre-screened)

The user received Copilot feedback on this topic. The technical substance is correct; a cleaned summary follows. **Important caveat:** several Copilot citations reference `forum.opencyphal.org` (OpenCyphal / UAVCAN v1/v2). INAV uses `dronecan/libcanard` (UAVCAN v0) — a different library. General patterns translate, but any specific API names must be verified against INAV's actual vendored libcanard, not OpenCyphal libcanard v2.

**Copilot's core recommendations (verified correct):**

- Use `FDCAN_TX_QUEUE_OPERATION` — Queue mode selects by CAN ID priority; FIFO mode does not
- Set `MAX_IN_HW_PENDING = 1` initially; relax to 2 only after bus-load testing
- Use `HAL_FDCAN_AddMessageToTxFifoQ()` — this IS the correct STM32 HAL function name (named "FifoQ" because the H7 RM calls the block "TX FIFO/Queue"; queue mode is selected by the TFQM bit)
- pump_tx() pattern:
  ```
  pump_tx()
    while in_hw_pending < MAX_IN_HW_PENDING:
      f = canardPeekTxQueue()   // verify actual fn name in INAV's libcanard
      if f == NULL: break
      if no room in FDCAN HW: break
      HAL_FDCAN_AddMessageToTxFifoQ(...)
      canardPopTxQueue()        // verify actual fn name
      in_hw_pending++
  ```
- Call pump_tx() after every libcanard enqueue AND after every TX-complete ISR event
- Bus-off: stop pumping until recovery; then call pump_tx() again

The recommended flow:
```
Application
  │  canardBroadcast() / request / respond
  ▼
libcanard TX queue (priority-sorted by CAN ID)
  │  pump_tx() — push head of queue to HW
  ▼
STM32H743 FDCAN TX Queue (shallow: 1–2 frames)
  │
  ▼
CAN bus arbitration (per frame, lowest ID = highest priority wins)
```

libcanard is the master scheduler; the peripheral is a small staging area only.

## Files to Check

- `inav/src/main/drivers/bus_can_stm32h7.c` (or equivalent — locate via `rg FDCAN_TX`)
- `inav/src/main/drivers/bus_can_stm32f7.c` (or equivalent for F7)
- `inav/src/main/flight/canard_dronecan.c` (or wherever libcanard TX queue is driven)
- PR #11560 branch: `feature/stm32f7-can-tx-isr`
- Vendored libcanard headers for actual TX queue API names

## Success Criteria

- [ ] H743 FDCAN TX mode confirmed — if FIFO, changed to Queue mode
- [ ] H743 hardware queue depth confirmed shallow (1–2 frames)
- [ ] F765 SW queue in #11560 confirmed priority-ordered (or issue filed on #11560)
- [ ] pump_tx() call sites verified correct (post-enqueue + post-TX-complete)
- [ ] Findings documented
- [ ] Any code changes build clean on F4, F7, H7, AT32, SITL

## Project Directory

`claude/projects/active/investigate-dronecan-tx-priority-queue/`

---
**Manager**

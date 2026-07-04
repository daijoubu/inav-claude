# Project: Investigate DroneCAN TX Priority — FIFO vs Queue and Queue Depth

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Investigation
**Created:** 2026-06-11
**Estimated Time:** 3–5 hours

## Overview

Audit the DroneCAN TX path on both STM32H743 (FDCAN hardware) and STM32F765 (bxCAN + software queue from PR #11560) to verify priority-preserving behaviour. Produce concrete recommendations — and code changes if warranted.

## Problem

DroneCAN encodes transfer priority in the CAN arbitration ID. Bus arbitration enforces priority between nodes, but **within a single node**, if the hardware or software TX queue dispatches frames in insertion order (FIFO) rather than by CAN ID, newly arrived high-priority frames can be stuck behind older low-priority ones already staged — priority inversion. This undermines DroneCAN's design intent.

Two specific concerns:

1. **H743 FDCAN hardware:** Does INAV configure the FDCAN TX block in Queue mode (`FDCAN_TX_QUEUE_OPERATION`) or FIFO mode? Queue mode selects the pending frame with the smallest CAN ID (highest priority) when multiple frames are staged; FIFO mode ignores ID ordering entirely. If FIFO mode is in use, priority inversion is possible whenever more than one frame is pending in hardware.

2. **F765 bxCAN (PR #11560):** The F7 ISR TX branch introduces a software TX queue for the F765. Does that queue dispatch in priority order (by CAN ID), or in insertion order? How deep is it? Similar inversion risk applies here if it's a plain FIFO.

## Objectives

1. Confirm (or correct) H743 FDCAN TX mode — Queue vs FIFO.
2. Confirm (or correct) hardware queue depth for H743 — should be kept shallow (1–2 frames) so libcanard retains scheduling control.
3. Review F765 SW queue in PR #11560 for the same priority-ordering property and depth.
4. Verify processCanardTxQueue() trigger points: called after libcanard enqueue AND after TX-complete ISR.
5. Document findings and produce a recommendation (with any code changes needed).

## Scope

**In Scope:**
- `inav/src/main/drivers/bus_can_stm32h7.c` (or equivalent H7 FDCAN driver)
- PR #11560 (`feature/stm32f7-can-tx-isr`) — F765 SW queue implementation
- libcanard TX queue API usage in INAV (`canardPeekTxQueue` / `canardPopTxQueue` — verify actual function names against vendored libcanard headers)
- processCanardTxQueue() pattern and call sites

**Out of Scope:**
- RX path
- DroneCAN protocol changes
- F4 / AT32 targets (bxCAN, no priority queue concern at hardware level in same way)

## Copilot Guidance (pre-reviewed)

Copilot provided detailed guidance on the recommended H743 FDCAN TX pattern. The substance is correct; see the task assignment for the cleaned-up version. **One important caveat:** several Copilot citations reference `forum.opencyphal.org` (OpenCyphal / UAVCAN v1/v2 community). INAV uses `dronecan/libcanard` (UAVCAN v0) — a different library with different API names. The general pump patterns and queue-depth philosophy translate, but any specific API names or signatures must be cross-checked against the actual libcanard headers vendored in INAV, not against OpenCyphal libcanard v2.

## Success Criteria

- [ ] H743 FDCAN TX mode confirmed — if FIFO, changed to Queue mode
- [ ] H743 hardware queue depth confirmed shallow (1–2 frames)
- [ ] F765 SW queue in #11560 confirmed priority-ordered (or issue filed on #11560)
- [ ] processCanardTxQueue() call sites verified correct (post-enqueue + post-TX-complete)
- [ ] Written findings document or inline comments explain the reasoning
- [ ] Any code changes build clean on F4, F7, H7, AT32, SITL

## Estimated Time

3–5 hours

## Priority Justification

Multiple in-flight DroneCAN features (GPS, magnetometer, node stats, DNA server) will all share this TX path. Fixing a priority inversion now — before those PRs land — is far cheaper than debugging sporadic priority issues post-merge under load.

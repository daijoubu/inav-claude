# Project: STM32F7 CAN TX ISR Migration

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM-HIGH
**Type:** Feature / Bug Fix
**Created:** 2026-04-26
**Estimated Effort:** 4-8 hours

## Overview

Migrate the STM32F7 CAN peripheral TX implementation from polling/blocking to interrupt-driven (ISR) transmission.

## Problem

The current STM32F7 CAN TX implementation causes:
- TX stalls under load
- Latency spikes
- Multi-frame packets transmitting out of sequence (suspected)

These issues degrade DroneCAN reliability, particularly for multi-frame transfers where ordering matters.

## Solution

Replace polling/blocking TX with an ISR-driven approach, matching the pattern used in other STM32 CAN implementations. The ISR handles mailbox-empty events and queues frames in order, eliminating stalls and ensuring correct sequencing.

## Implementation

- Locate STM32F7 CAN driver in `inav/src/main/drivers/` (likely `canbus_stm32f7xx.c` or similar)
- Understand current TX approach (polling vs mailbox management)
- Implement TX ISR handler for CAN TX mailbox empty interrupts
- Add TX queue if not present to buffer outgoing frames
- Enable TX interrupts in CAN peripheral init
- Verify multi-frame DroneCAN transfers maintain sequence

## Success Criteria

- [ ] `LOG_DEBUG` removed/guarded in `canardSTM32Transmit()` line 166 (hard blocker — ISR context)
- [ ] Verbose logging reduced in `canardSTM32ComputeTimings()` and `dronecan.c` transfer handler
- [ ] CAN TX uses ISR rather than polling/blocking
- [ ] No TX stalls under normal DroneCAN load
- [ ] Multi-frame transfers maintain correct frame order
- [ ] Firmware builds cleanly for affected F7 targets
- [ ] DroneCAN GPS and other nodes operate correctly after change
- [ ] PR created targeting `maintenance-10.x`

## Related

- **Assignment:** `manager/email/sent/2026-04-26-1600-task-feature-stm32f7-can-tx-isr.md`
- **Repository:** inav (firmware) | **Branch:** `maintenance-10.x`

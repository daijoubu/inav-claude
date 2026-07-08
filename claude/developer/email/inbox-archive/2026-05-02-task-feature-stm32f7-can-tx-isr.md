# Task Assignment: STM32F7 CAN TX ISR Migration

**Date:** 2026-05-02
**From:** Manager
**To:** Developer
**Project:** feature-stm32f7-can-tx-isr
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4–8 hours

## Task

Migrate the STM32F7 CAN TX implementation from polling/blocking to ISR-driven transmission to fix TX stalls, latency spikes, and suspected out-of-order multi-frame DroneCAN packet delivery.

## Background

The current STM32F7 CAN TX driver blocks while waiting for a mailbox to become free. Under DroneCAN load this causes stalls and latency spikes. Multi-frame transfers (e.g. NodeStatus, large transfers) are suspected to arrive out of sequence as a result. Migrating to an ISR-driven TX approach — matching what F4/H7 already do — should eliminate these problems.

## What to Do

Full task breakdown is in `claude/projects/active/feature-stm32f7-can-tx-isr/todo.md`. Summary:

### Phase 0: LOG_DEBUG cleanup (do this first)
- Remove/replace `LOG_DEBUG` in `canardSTM32Transmit()` line 166 — **hard blocker**, calling printf from ISR context is undefined behaviour
- Reduce verbose LOG_DEBUG in `canardSTM32ComputeTimings()` (6 calls → 1 summary)
- Gate per-frame LOG_DEBUG in `dronecan.c` transfer handler (~10 calls that fire on every received frame)

### Phase 1: Investigate
- Locate the STM32F7 CAN driver (`canbus_stm32f7xx.c` or similar in `src/main/drivers/`)
- Understand current TX approach
- Check how F4/H7 CAN TX ISR is implemented for reference

### Phase 2: Implement
- Implement TX ISR handler for CAN TX mailbox empty interrupts
- Add TX queue if needed
- Enable TX interrupts in CAN peripheral init
- Remove/replace blocking TX polling

### Phase 3: Validate
- Builds cleanly for F7 targets
- DroneCAN GPS operates correctly
- Multi-frame transfers verified in order

## Success Criteria

- [ ] LOG_DEBUG removed/guarded in canardSTM32Transmit() (ISR safety)
- [ ] Verbose logging reduced before upstream submission
- [ ] CAN TX uses ISR rather than polling
- [ ] No TX stalls under normal DroneCAN load
- [ ] Multi-frame transfers maintain correct frame order
- [ ] Builds cleanly for affected F7 targets
- [ ] PR created targeting maintenance-10.x

## Project Directory

`claude/projects/active/feature-stm32f7-can-tx-isr/`

## Branch

New branch off `maintenance-10.x` → PR targets `maintenance-10.x`

---
**Manager**

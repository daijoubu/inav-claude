# Task Assignment: STM32F7 CAN TX ISR Migration

**Date:** 2026-04-26 16:00
**From:** Manager
**To:** Developer
**Project:** feature-stm32f7-can-tx-isr
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 4-8 hours

## Task

Migrate the STM32F7 CAN TX implementation from polling/blocking to ISR-driven transmission.

## Background

The current STM32F7 CAN TX approach is causing:
- TX stalls under load
- Latency spikes
- Multi-frame packets suspected to transmit out of sequence

These degrade DroneCAN reliability, particularly for multi-frame transfers where ordering matters.

## What to Do

1. Locate the STM32F7 CAN driver (likely `src/main/drivers/` — look for `canbus_stm32f7xx.c` or similar)
2. Review the current TX implementation to understand polling/mailbox approach
3. Reference any F4 or H7 CAN TX ISR implementation as a pattern
4. Implement ISR handler for CAN TX mailbox-empty interrupts
5. Add/extend a TX queue if needed to buffer outgoing frames in order
6. Enable TX interrupts in CAN peripheral init
7. Build and test on an F7 target with DroneCAN devices attached

## Success Criteria

- [ ] CAN TX uses ISR rather than polling/blocking
- [ ] No TX stalls under normal DroneCAN load
- [ ] Multi-frame transfers maintain correct frame order
- [ ] Firmware builds cleanly for affected F7 targets
- [ ] DroneCAN GPS and other nodes operate correctly after change
- [ ] PR created targeting `maintenance-10.x`

## Project Directory

`claude/projects/active/feature-stm32f7-can-tx-isr/`

## Branch

New branch off `maintenance-10.x` → PR targets `maintenance-10.x`

---
**Manager**

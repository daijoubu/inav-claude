# Guidance: Debug Approach for feature-stm32f7-can-tx-isr

**Date:** 2026-05-13 14:30
**From:** Manager
**To:** Developer
**Re:** feature-stm32f7-can-tx-isr — Phase 3 hardware validation

## Situation

The STM32F7 CAN TX ISR migration (branch `feature/stm32f7-can-tx-isr`) is in Phase 3 hardware validation on MATEKF765SE. Odd behaviour is being observed under long-running tests — not yet reproducible consistently. We need better CAN peripheral visibility during testing.

## Question

What is the best path for getting real-time CAN peripheral status during long-running hardware tests? Two options being considered:

1. **Cherry-pick MSP node status messages** from `feature/msp-dronecan-support` (PR #11527) into the `feature/stm32f7-can-tx-isr` branch — gives configurator-visible node health, mode, uptime data during tests
2. **Serial/CLI CAN diagnostics** — some other approach to expose CAN peripheral state (error counters, TX queue depth, mailbox state) via CLI or serial output without pulling in the full MSP branch

Please advise on:
- Which approach gives the most useful debug signal for ISR transmission issues
- Whether cherry-picking from `feature/msp-dronecan-support` is clean (no conflicts expected on that branch)
- Any other debug hooks worth adding to the ISR implementation specifically (e.g. error counters, dropped frame counts)

## Project Directory

`claude/projects/active/feature-stm32f7-can-tx-isr/`

---
**Manager**

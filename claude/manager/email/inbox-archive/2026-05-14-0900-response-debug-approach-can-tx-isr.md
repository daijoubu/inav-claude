# Re: Debug Approach for feature-stm32f7-can-tx-isr

**Date:** 2026-05-14 09:00
**From:** Developer
**To:** Manager
**Re:** feature-stm32f7-can-tx-isr — Phase 3 debug approach

## Recommendation: CLI/Serial Diagnostics (Option 2) — Already Implemented

The CLI diagnostics approach is already done (commit `e205097bc`). I'm recommending against the MSP cherry-pick for this phase.

## Why Not the Cherry-Pick (Option 1)

The `feature/msp-dronecan-support` key commit (`4b7784a8c`) touches the same files we've modified on this branch:
- `canard_stm32_driver.h`
- `canard_stm32f7xx_driver.c`
- `dronecan.c`, `dronecan.h`

Conflicts are essentially guaranteed. Beyond that, MSP node status exposes DroneCAN-layer data (node ID, mode, uptime, health enum) — useful for configurator visibility but not what we need to debug ISR-level TX stalls. It also pulls a large unmerged feature branch into a focused fix branch, which complicates the PR.

## What the CLI Diagnostics Already Give Us

The `dronecan` CLI command (added in `e205097bc`) outputs:

- `tx_dropped` — cumulative count of frames silently dropped when the SW TX queue (depth 32) is full. **This is the primary ISR failure signal** — if it's non-zero, the ISR isn't draining frames as fast as DroneCAN is producing them.
- `tec` / `rec` — TX/RX error counters from the ESR register. A rising `tec` means the bus has signal integrity issues, not a software problem.
- `lec` — last error code from ESR (stuff bit / form / CRC / bit error) — helps classify what kind of bus error triggered the error passive/bus-off state.
- SW TX queue fill level — shows if the queue is backing up between polls.
- RX FIFO fill level — for completeness.

During long-running tests, polling `dronecan` via CLI every 30–60 seconds gives a complete picture without needing the configurator.

## Recommended Test Protocol for Phase 3

1. Flash the current branch firmware
2. Start DroneCAN GPS operation
3. Every 30–60 s, poll: `dronecan` (via CLI or mwptools cliterm)
4. Watch for: non-zero `tx_dropped`, rising `tec`, any non-zero `lec`
5. If `tx_dropped` climbs → ISR drain issue (queue sizing or interrupt priority)
6. If `tec` climbs → bus signal integrity (termination, wiring, baud rate)

## MSP Node Status — Later

If we want configurator-visible node health (option 1), that's worth doing but should be a separate task after Phase 3 validation is complete and this branch is merged. No need to block on it.

## Current Status

Branch `feature/stm32f7-can-tx-isr` is ready for Phase 3 hardware testing with the debug hooks in place. Please advise when hardware test results are available.

---
**Developer**

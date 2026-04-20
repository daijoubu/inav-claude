# Todo: Investigate Bidir DShot Simultaneous Motor RX

## Phase 1: ESC Response Timing

- [x] Determine GCR response window: when do ESCs start/finish responding after DShot frame?
- [x] Is response timing deterministic enough for simultaneous IC trigger?
- [x] Check if response windows overlap across motors (same timer vs. different timers)

## Phase 2: Timer / Hardware Mechanics

- [x] Can multiple OC channels on one timer switch to IC simultaneously (single register write)?
- [x] What triggers the IC capture for simultaneous multi-channel RX?
- [x] STM32H7 DMAMUX: does it help or complicate simultaneous IC DMA?

## Phase 3: DMA Resource Analysis

- [x] Count DMA streams needed for simultaneous 4-motor IC capture
- [x] Compare to per-channel sequential approach (same or more resources?)
- [x] Check DMA resource budget on key H7 targets (MATEKH743, KAKUTEH7)

## Phase 4: Betaflight Research

- [x] Review BF dshot_bidir.c for sequential vs. simultaneous design rationale
- [x] Search BF commit history / PRs for any discussion of simultaneous RX
- [x] Check if BF's per-channel approach was a deliberate choice or default

## Phase 5: Verdict

- [x] Write clear YES/NO on simultaneous RX feasibility
- [x] If YES: outline revised implementation approach for feature-bidirectional-dshot-h7
- [x] If NO: confirm current sequential/DMAR-exclusive plan is correct
- [x] Send completion report to manager

## Completion

- [x] Research findings documented in project directory (findings.md)
- [ ] Completion report sent to manager

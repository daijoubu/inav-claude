# Todo: Investigate DroneCAN TX Priority — FIFO vs Queue and Queue Depth

## Phase 1: Audit

- [ ] Locate H743 FDCAN driver — find the TX mode configuration (`TxFifoQueueMode`)
  - [ ] Record current setting: FIFO or Queue mode?
  - [ ] Find how many frames are staged into hardware at once (queue depth)
- [ ] Locate processCanardTxQueue() equivalent (or equivalent inlining) in H7 driver
  - [ ] Is it called after libcanard enqueue?
  - [ ] Is it called after TX-complete ISR/callback?
- [ ] Check out PR #11560 branch (`feature/stm32f7-can-tx-isr`) and audit F765 SW queue
  - [ ] Is the SW queue ordered by CAN ID (priority), or insertion order (FIFO)?
  - [ ] What is the queue depth?
  - [ ] Does processCanardTxQueue() pattern apply here too?
- [ ] Verify actual DroneCAN libcanard TX queue API names in INAV's vendored libcanard
  - [ ] Confirm `canardPeekTxQueue` / `canardPopTxQueue` (or note actual names)

## Phase 2: Recommendations and Fixes

- [ ] H743 FDCAN driver
  - [ ] If FIFO mode: change to `FDCAN_TX_QUEUE_OPERATION`
  - [ ] If depth > 2: reduce to 1 (or 2 if justified), note rationale
  - [ ] If processCanardTxQueue() call sites are missing: add them
- [ ] F765 SW queue in PR #11560
  - [ ] If insertion-ordered: either file a note on the PR or propose a fix
  - [ ] If depth is too deep: flag it
- [ ] Write up findings — a brief inline comment block or a findings note in this directory

## Phase 3: Verify

- [ ] Any code changes build clean: F4, F7, H7, AT32, SITL
- [ ] No regressions in existing CAN/DroneCAN behaviour

## Completion

- [ ] Findings documented
- [ ] Code changes (if any) committed on appropriate branch
- [ ] Completion report sent to manager

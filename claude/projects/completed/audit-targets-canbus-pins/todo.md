# Todo: Audit AP H7/F7 Targets — Add CAN Bus Pins to INAV Targets

## Phase 1: Audit

- [ ] List all H7 INAV targets (`src/main/target/` — search for STM32H7)
- [ ] List all F7 INAV targets (search for STM32F7)
- [ ] For each target, find the corresponding ArduPilot board definition in `ArduPilot/`
- [ ] Extract CAN RX/TX pin assignments from each AP definition
- [ ] Build a mapping table: INAV target → AP board → CAN1_RX, CAN1_TX, CAN2_RX, CAN2_TX
- [ ] Note any INAV targets with no AP equivalent (skip those)
- [ ] Note any targets that already have CAN pins defined in INAV

## Phase 2: Implementation

- [ ] For each target with a pin mapping found:
  - Add commented-out CAN pin block to `target.h`
  - Follow convention: `// CAN bus pins — sourced from ArduPilot`
- [ ] KAKUTEH7WING — add pins uncommented (tested hardware, do not comment out)
- [ ] Verify no target already defines conflicting pins

## Phase 3: Verify

- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL) — commented pins must not break builds
- [ ] KAKUTEH7WING builds with CAN pins active
- [ ] Spot-check 2-3 other targets to confirm commented blocks are inert

## Completion

- [ ] PR created to `maintenance-10.x`
- [ ] Completion report sent to manager — include the mapping table and any targets skipped

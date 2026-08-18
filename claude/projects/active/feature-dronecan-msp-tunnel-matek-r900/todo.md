# Todo List: MSP Tunneling over DroneCAN for Matek R900-30C

## Phase 1: Document + Failing Test

- [ ] Write user-facing documentation describing how MSP tunneling over
      DroneCAN works: which `uavcan.tunnel.*` messages are used, how a CAN
      node is addressed, what INAV exposes as the bridge endpoint
- [ ] Write a failing test (SITL scenario or mocked tunnel node) that
      exercises an MSP request/response tunneled over a simulated CAN node
- [ ] Confirm the test fails for the right reason (feature not yet
      implemented, not a setup error)

## Phase 2: Implementation

- [ ] Implement `uavcan.tunnel.Broadcast`/`Targetted` handling in the
      DroneCAN driver (`src/main/drivers/dronecan/dronecan.c`)
- [ ] Bridge tunneled MSP payloads to/from an INAV MSP endpoint (virtual MSP
      port, or relay through `src/main/msp/msp_serial.c` dispatch — evaluate
      which fits existing architecture)
- [ ] Handle `uavcan.tunnel.Protocol`/framing correctly for MSPv1 and MSPv2
- [ ] Confirm behavior when the addressed node is absent/unresponsive

## Phase 3: Verify

- [ ] Failing test from Phase 1 now passes
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Hardware-verify against a real Matek R900-30C: MSP request/response
      round-trips correctly over the CAN tunnel
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md`)
- [ ] Completion report sent to manager

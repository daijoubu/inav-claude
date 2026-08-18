# Todo List: DroneCAN ESC Control

## Phase 1: Document + Failing Test

- [ ] Write user-facing documentation: how to select DroneCAN ESC output,
      how motor index maps to ESC DroneCAN index, exact fail-safe behavior
      on CAN loss/bus-off/disarm
- [ ] Write a failing test (SITL scenario or mocked CAN node) that exercises
      mixer motor output → `esc.RawCommand` broadcast end-to-end
- [ ] Confirm the test fails for the right reason (feature not yet
      implemented, not a setup error)

## Phase 2: Implementation

- [ ] Add DroneCAN ESC output path: broadcast `esc.RawCommand` from
      `motor[]` values (`src/main/flight/mixer.h`), scaled correctly to the
      message's int14 range
- [ ] Determine and implement appropriate broadcast rate for real-time motor
      control (not sensor-loop rate)
- [ ] Add motor index → DroneCAN ESC index mapping and output-type selection
      alongside existing PWM/DShot motor protocols
- [ ] Implement fail-safe: correct behavior on CAN bus-off, node
      absence/timeout, and arm/disarm transitions
- [ ] Add CLI setting; check Configurator support needed

## Phase 3: Verify

- [ ] Failing test from Phase 1 now passes
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Hardware-verify against a real DroneCAN ESC — confirm commanded values
      match, confirm fail-safe triggers correctly on CAN loss
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md`)
- [ ] Completion report sent to manager

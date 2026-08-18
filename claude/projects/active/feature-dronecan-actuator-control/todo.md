# Todo List: DroneCAN Actuator Control

## Phase 1: Document + Failing Test

- [x] Write user-facing documentation: how to select DroneCAN servo output,
      how servo index maps to `actuator_id`, which `command_type` is used
      and why, exact fail-safe behavior on CAN loss/bus-off/disarm
      (`docs.md`, 2026-08-13)
- [x] Write a failing test (SITL scenario or mocked CAN node) that exercises
      mixer servo output → `actuator.ArrayCommand` broadcast end-to-end
      (`src/test/unit/dronecan_actuator_output_unittest.cc`, 2026-08-14)
- [x] Confirm the test fails for the right reason (feature not yet
      implemented, not a setup error) — confirmed via loopback-receiver
      harness + passing sanity test proving the rig itself works

## Phase 2: Implementation

- [ ] Add DroneCAN actuator output path: broadcast `actuator.ArrayCommand`
      from mixer servo output values, correctly encoding `actuator_id` +
      `command_type` + `command_value`
- [x] Decide `command_type` (POSITION vs PWM vs other) based on target
      hardware expectations; document the choice (`PWM`, `docs.md`,
      2026-08-13 — AP_Periph doesn't implement `COMMAND_TYPE_POSITION`)
- [ ] Add servo index → actuator ID mapping and output-type selection
      alongside existing local PWM servo output
- [ ] Implement fail-safe: correct behavior on CAN bus-off, node
      absence/timeout, and arm/disarm transitions
- [ ] Add CLI setting; check Configurator support needed
- [x] Broadcast `ardupilot_indication_SafetyState` for AP_Periph
      compatibility — AP_Periph hardware-disables PWM output at boot until
      this vendor-specific message is received; no runtime parameter or
      hwdef override exists to disable that requirement. Decided
      (`docs.md`, "AP_Periph safety-switch compatibility", 2026-08-14):
      broadcast at 2 Hz (matching ArduPilot's own reference sender's
      cadence) but always send `SAFETY_OFF` unconditionally — no toggling
      on arm state, matching the existing decision that servo actuators
      aren't arm-gated (motors/ESC arm-gating is the separate
      feature-dronecan-esc-control project's concern). Hardware-confirmed
      working, 2026-08-14

## Phase 3: Verify

- [ ] Failing test from Phase 1 now passes
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Hardware-verify against a real DroneCAN servo/actuator node — confirm
      commanded positions match, confirm fail-safe triggers correctly on
      CAN loss
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md`)
- [ ] Completion report sent to manager

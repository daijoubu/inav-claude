# Todo List: DroneCAN RCInput Support

## Phase 1: Document + Failing Test

- [ ] Write user-facing documentation describing the new DroneCAN receiver
      type: how to select it, what `sensors.rc.RCInput` fields map to which
      channels, failsafe behavior on stale data
- [ ] Write a failing test (unit test and/or SITL scenario) that exercises
      RCInput decode → `rxRuntimeState` end-to-end
- [ ] Confirm the test fails for the right reason (feature not yet
      implemented, not a setup error)

## Phase 2: Implementation

- [ ] Add `RX_TYPE_DRONECAN` (or equivalent) to `src/main/rx/rx.h`
- [ ] Subscribe to `sensors.rc.RCInput` in the DroneCAN driver, following the
      existing per-driver pattern (`gps_dronecan.c`,
      `battery_sensor_dronecan.c`)
- [ ] Decode channel array + status/quality fields into `rxRuntimeState`
- [ ] Wire new type into `rx.c` provider init/update dispatch
- [ ] Add CLI setting to select DroneCAN as receiver type; check
      Configurator support needed
- [ ] Implement failsafe/link-quality handling for stale or missing RCInput
      broadcasts

## Phase 3: Verify

- [ ] Failing test from Phase 1 now passes
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Hardware-verify against a real CAN RC source (R900-30C or other
      RCInput-publishing node)
- [ ] Confirm failsafe triggers correctly when the CAN RC link drops
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md`)
- [ ] Completion report sent to manager

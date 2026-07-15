# Todo: Fix MSP Servo Mixer targetChannel Bounds Check

## Phase 1: Reproduce (bug fix)

- [ ] Send `MSP_SET_SERVO_MIX_RULE` with `targetChannel >= MAX_SUPPORTED_SERVOS`
      (e.g. via SITL/mspapi2) and confirm it is accepted with no error
- [ ] Send `MSP2_INAV_SET_SERVO_MIXER` with the same out-of-range value and
      confirm the same acceptance
- [ ] Confirm root cause — trace the accepted value through
      `loadCustomServoMixer()` into the mixing loop's array indexing to
      confirm the OOB access

## Phase 2: Implementation

- [ ] Add `targetChannel < MAX_SUPPORTED_SERVOS` check to
      `MSP_SET_SERVO_MIX_RULE` handler (`fc/fc_msp.c:2469-2481`), returning
      `MSP_RESULT_ERROR` on failure
- [ ] Add the same check to `MSP2_INAV_SET_SERVO_MIXER` handler
      (`fc/fc_msp.c:2483-2489`)
- [ ] Add unit tests covering both handlers rejecting an out-of-range
      `targetChannel`

## Phase 3: Verify

- [ ] Confirm both handlers now reject `targetChannel >= MAX_SUPPORTED_SERVOS`
- [ ] Confirm valid `targetChannel` values (0 through
      `MAX_SUPPORTED_SERVOS - 1`) still work unchanged
- [ ] Confirm the CLI path (`cliServoMix()`) is unaffected

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager

# Todo List: Fix Fragile Hand-Mirrored Unit Tests

## Phase 1: pwm_mapping_beeper_unittest.cc

- [ ] Add `TIM_USE_PINIO` to the mirrored `timerUsageFlag_e` enum
- [ ] Update mirrored `OUTPUT_MODE_PINIO` case to set `TIM_USE_PINIO`,
      matching `pwm_mapping.c:232-235`
- [ ] Add/update assertions so `FixVerification_BeeperProtectedFromPinioOverride`
      and `PinioOverride_ClearsAllOutputFlags` actually check `TIM_USE_PINIO`
- [ ] Evaluate whether `timerHardwareOverride()` can be extracted from its
      `#ifndef SITL_BUILD` guard and linked directly instead of mirrored

## Phase 2: pwm_output_assignment_unittest.cc

- [ ] Fix or replace `TimerHwMaxGuard.OutRemainsZeroWhenCountExceedsLimit`
      so it actually exercises the `TIMER_HW_MAX` guard
- [ ] Evaluate whether `pwmCalculateAssignment()` can be extracted from its
      `#ifndef SITL_BUILD` guard and linked directly instead of mirrored
- [ ] Re-verify the payload-validation mirror still matches
      `fc_msp.c:4884-4906` after any restructuring

## Completion

- [ ] Full unit test suite passing
- [ ] Completion report sent to manager

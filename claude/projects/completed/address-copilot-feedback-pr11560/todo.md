# Todo: Address Copilot Review Feedback on PR #11560

## Phase 1: Investigate & Fix

- [ ] Review all 6 Copilot comments in detail
- [ ] Fix H7 RX overflow: validate/clamp `RxHeader.DataLength` <= 8 in `canard_stm32h7xx_driver.c`
- [ ] Fix H7 TX overflow: bounds check `TxHeader.DataLength` in `canard_stm32h7xx_driver.c`
- [ ] Fix F7 TX bounds: validate/clamp `frame->data_len <= 8` in `canard_stm32f7xx_driver.c`
- [ ] Fix ATOMIC_BLOCK comment accuracy in `canard_stm32f7xx_driver.c`
- [ ] Fix stale unique ID comment in `dronecan.c`
- [ ] Address ring buffer capacity (31 vs 32) in `canard_stm32f7xx_driver.c`

## Phase 2: Build & Test

- [ ] Build F7 target (MATEKF765SE)
- [ ] Build H7 target (MATEKH743)
- [ ] Build SITL
- [ ] Verify no regressions

## Phase 3: Submit

- [ ] Commit fixes to PR branch
- [ ] Reply to each Copilot comment noting the fix
- [ ] Notify PR author (daijoubu)

## Completion

- [ ] All Copilot comments resolved
- [ ] Builds pass on all affected targets
- [ ] Completion report sent to manager

# Todo: STM32F4 HAL Macro Redefinition Warnings Fix

## Phase 1: Implementation

- [ ] Review commit `37e6b23ea` (`cmake/stm32f7.cmake` fix) for exact change needed
- [ ] Apply same `SYSTEM_INCLUDE_DIRECTORIES` treatment to `cmake/stm32f4.cmake`
- [ ] Commit onto `feature/stm32f7-hal-v1.3.3-update` branch

## Phase 2: Verification

- [ ] Build `SPEEDYBEEF405WING` (F4) — must pass with no `__FPU_PRESENT` warnings
- [ ] Build `MATEKF765SE` (F7) — must still pass
- [ ] Build `MATEKH743` (H7) — must still pass
- [ ] Build SITL — must still pass

## Completion

- [ ] All four MCU families building cleanly
- [ ] Send completion report to manager

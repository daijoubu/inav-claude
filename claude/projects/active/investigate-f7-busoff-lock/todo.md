# Todo List: Investigate F7 Permanent BUS_OFF Lock

## Phase 1: Research

- [ ] Read `canard_stm32f7xx_driver.c` — understand current `canardSTM32RecoverFromBusOff()` no-op and AutoBusOff config
- [ ] Review STM32F7 bxCAN reference manual section on init mode and ESR.BOFF
- [ ] Understand why `HAL_CAN_Stop/Start` caused lockup (interrupt context, blocking poll)
- [ ] Identify correct register sequence to re-enter init mode and exit, clearing ESR.BOFF

## Phase 2: Implementation

- [ ] Choose approach (direct register manipulation, deferred task, or IRQ-masked HAL call)
- [ ] Implement `canardSTM32RecoverFromBusOff()` with safe execution
- [ ] Add timeout/bounds to any blocking poll to prevent hang

## Phase 3: Testing

- [ ] Induce bus-off on MATEKF765SE (disconnect/short bus briefly)
- [ ] Confirm hardware recovery completes (128×11 sequence)
- [ ] Confirm ESR.BOFF is cleared after fix
- [ ] Confirm no scheduler lockup
- [ ] Normal operation resumes after recovery

## Completion

- [ ] All tests passing
- [ ] PR opened against `maintenance-10.x`
- [ ] Send completion report to manager

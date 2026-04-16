# DroneCAN HAL v1.3.3 Compatibility Issue

## Problem

The DroneCAN driver (`src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`) was written against STM32F7 HAL v1.2.2 CAN API. HAL v1.3.3 introduced a breaking change to the CAN peripheral API.

**Build Status:** ❌ FAILS - 40+ compilation errors in DroneCAN driver

## Root Cause

STM32F7 HAL v1.3.3 completely restructured the CAN driver API:

### API Changes Required

| Old API (v1.2.2) | New API (v1.3.3) | Location |
|---|---|---|
| `CanRxMsgTypeDef` | `CAN_RxHeaderTypeDef` + payload | Separate structs |
| `CanTxMsgTypeDef` | `CAN_TxHeaderTypeDef` + payload | Separate structs |
| `hcan1.pTxMsg` | `HAL_CAN_AddTxMessage()` | Function call |
| `HAL_CAN_Transmit()` | `HAL_CAN_AddTxMessage()` | Different API |
| `CAN_FilterConfTypeDef` | `CAN_FilterTypeDef` | Struct rename |
| Init: `TTCM`, `ABOM`, `AWUM`, `NART`, `RFLM`, `TXFP` | Init: `TimeTriggeredMode`, `AutoBusOff`, `AutoWakeUp`, `AutoRetransmission`, `ReceiveFifoLocked`, `TransmitFifoPriority` | Struct members |
| `HAL_CAN_RxCpltCallback()` | `HAL_CAN_RxFifo0MsgPendingCallback()` | IRQ callback |

## Fix Required

Update `canard_stm32f7xx_driver.c` to use the new HAL CAN API:

### Key Changes
1. **RX Buffer:** Change from `CanRxMsgTypeDef` array to separate header + payload buffers
2. **TX:** Use `HAL_CAN_AddTxMessage()` with `CAN_TxHeaderTypeDef`
3. **RX:** Use `HAL_CAN_GetRxMessage()` with `CAN_RxHeaderTypeDef`
4. **Init:** Update `CAN_InitTypeDef` struct initialization with new member names
5. **Filters:** Update filter configuration for new `CAN_FilterTypeDef`
6. **Callbacks:** Update IRQ handler to use new callback name

## Testing Strategy

After fixing `canard_stm32f7xx_driver.c`:
1. Build MATEKF765 target
2. Flash to MATEKF765-WSE
3. Verify DroneCAN battery monitor is detected
4. Check for any CAN communication errors
5. Run Phase 4 hardware tests

## Branch

- **Branch:** `feature/stm32f7-hal-v1.3.3-update`
- **HAL Update Commit:** `2a8705061`
- **DroneCAN Merge:** `69a1352a2`

## References

- STM32F7xx HAL CAN API: `lib/main/STM32F7/Drivers/STM32F7xx_HAL_Driver/Inc/stm32f7xx_hal_can.h`
- DroneCAN Driver: `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`

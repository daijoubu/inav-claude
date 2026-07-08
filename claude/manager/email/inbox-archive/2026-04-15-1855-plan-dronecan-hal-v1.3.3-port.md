# Plan: Port DroneCAN Driver to STM32F7xx HAL v1.3.3

**Date:** 2026-04-15 17:55 | **From:** Developer | **To:** Manager | **Type:** Implementation Plan

## Background

During the STM32F7xx HAL update (v1.2.2 → v1.3.3), we discovered that the DroneCAN driver is incompatible with the new HAL CAN API. The HAL v1.3.3 completely restructured the CAN peripheral interface.

**Branch with HAL update:** `feature/stm32f7-hal-v1.3.3-update`
**File requiring changes:** `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`
**Build errors:** 40+ compilation errors, all in this one file

## Scope of Changes

All changes are confined to **one file**: `canard_stm32f7xx_driver.c` (~456 lines)

---

## Phase 1: Data Structures (0.5 hrs)

**Problem:** `CanRxMsgTypeDef` and `CanTxMsgTypeDef` no longer exist. The new API separates header and payload.

**Changes:**

```c
// OLD RX Buffer
CanRxMsgTypeDef rxMsg[RX_BUFFER_SIZE];

// NEW RX Buffer — separate header and data
typedef struct {
    CAN_RxHeaderTypeDef header;
    uint8_t data[8];
} RxFrame_t;
RxFrame_t rxMsg[RX_BUFFER_SIZE];
```

Update `rxBufferPushFrame()` and `rxBufferPopFrame()` to use `RxFrame_t` instead of `CanRxMsgTypeDef`.

---

## Phase 2: Receive Function (0.5 hrs)

**Problem:** `canardSTM32Recieve()` and the RX interrupt callback use old struct field access patterns. Data is now separate from the header.

**Changes to `canardSTM32Recieve()`:**
```c
// OLD
rx_frame->data_len = canRxFrame.DLC;
memcpy(rx_frame->data, canRxFrame.Data, canRxFrame.DLC);

// NEW
rx_frame->data_len = canRxFrame.header.DLC;
memcpy(rx_frame->data, canRxFrame.data, canRxFrame.header.DLC);
```

**Changes to `HAL_CAN_RxCpltCallback()` → `HAL_CAN_RxFifo0MsgPendingCallback()`:**
```c
// OLD callback signature and body
void HAL_CAN_RxCpltCallback(CAN_HandleTypeDef *hcan) {
    rxBufferPushFrame(&RxBuffer, hcan1.pRxMsg);
    __HAL_CAN_ENABLE_IT(hcan, CAN_IT_FMP0);
}

// NEW — use HAL_CAN_GetRxMessage to fetch from FIFO
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    RxFrame_t frame;
    if (HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &frame.header, frame.data) == HAL_OK) {
        rxBufferPushFrame(&RxBuffer, &frame);
    }
}
```

---

## Phase 3: Transmit Function (0.5 hrs)

**Problem:** `CanTxMsgTypeDef`, `hcan1.pTxMsg`, and `HAL_CAN_Transmit()` are removed.

**Changes to `canardSTM32Transmit()`:**
```c
// OLD
CanTxMsgTypeDef txMsg = {};
// ... populate txMsg fields ...
hcan1.pTxMsg = &txMsg;
returnCode = HAL_CAN_Transmit(&hcan1, 100);

// NEW
CAN_TxHeaderTypeDef txHeader = {};
uint8_t txData[8];
uint32_t txMailbox;
// ... populate txHeader fields (same field names) ...
memcpy(txData, tx_frame->data, tx_frame->data_len);
returnCode = HAL_CAN_AddTxMessage(&hcan1, &txHeader, txData, &txMailbox);
```

Note: Field names (IDE, ExtId, StdId, DLC, RTR) are the same in `CAN_TxHeaderTypeDef`, so the ID/format mapping logic does not change.

---

## Phase 4: CAN Initialization (1 hr)

**Problem:** `CAN_FilterConfTypeDef` renamed, `CAN_InitTypeDef` member names changed, and the start/interrupt sequence changed significantly.

**Filter struct rename:**
```c
// OLD
CAN_FilterConfTypeDef sFilterConfig;
sFilterConfig.FilterNumber = 0;

// NEW
CAN_FilterTypeDef sFilterConfig;
sFilterConfig.FilterBank = 0;
// BankNumber field removed
```

**Init struct member renames:**
```c
// OLD → NEW
hcan1.Init.TTCM  → hcan1.Init.TimeTriggeredMode
hcan1.Init.ABOM  → hcan1.Init.AutoBusOff
hcan1.Init.AWUM  → hcan1.Init.AutoWakeUp
hcan1.Init.NART  → hcan1.Init.AutoRetransmission  // ⚠️ Logic INVERTED: NART=DISABLE → AutoRetransmission=ENABLE
hcan1.Init.RFLM  → hcan1.Init.ReceiveFifoLocked
hcan1.Init.TXFP  → hcan1.Init.TransmitFifoPriority
```

**Timing register bit positions — use HAL enum values:**
```c
// OLD (raw bit shifts)
hcan1.Init.SJW = (out_timings.sjw << CAN_BTR_SJW_Pos);
hcan1.Init.BS1 = (out_timings.bs1 << CAN_BTR_TS1_Pos);
hcan1.Init.BS2 = (out_timings.bs2 << CAN_BTR_TS2_Pos);

// NEW (pass raw values — HAL v1.3.3 handles bit positioning internally)
hcan1.Init.SyncJumpWidth = out_timings.sjw;
hcan1.Init.TimeSeg1      = out_timings.bs1;
hcan1.Init.TimeSeg2      = out_timings.bs2;
```

**Start sequence — new API requires explicit start + notification enable:**
```c
// OLD
hcan1.pRxMsg = &rxMsg;           // pointer-based Rx buffer
HAL_CAN_Receive_IT(&hcan1, CAN_FIFO0);  // single-shot Rx interrupt

// NEW — explicit start and notification
HAL_CAN_Start(&hcan1);           // must explicitly start CAN peripheral
HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);  // persistent Rx notification
```

---

## Phase 5: Build & Test (1 hr)

1. Build MATEKF765 target — verify zero compilation errors
2. Flash to MATEKF765-WSE
3. Verify DroneCAN battery monitor detected and providing voltage/current data
4. Test error recovery (BUS_OFF, ERROR_PASSIVE states)
5. Run baseline SD card tests to confirm no regressions

---

## Estimated Effort

| Phase | Task | Hours |
|---|---|---|
| 1 | Data structures (RxFrame_t) | 0.5 |
| 2 | Receive function + callback | 0.5 |
| 3 | Transmit function | 0.5 |
| 4 | CAN initialization | 1.0 |
| 5 | Build verification + hardware test | 1.0 |
| **Total** | | **3.5 hrs** |

---

## Branch

Work on: `feature/stm32f7-hal-v1.3.3-update`
Reference: `DRONECAN_COMPATIBILITY.md` in project directory

---

**Developer**

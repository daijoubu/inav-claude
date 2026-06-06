# Investigation Findings: F7 bxCAN Bus-Off Recovery

**Date:** 2026-05-30
**Investigator:** Developer
**Reference:** RM0410 Rev 5 (STM32F76x/F77x Reference Manual)

## Verdict: No-op is CORRECT

`canardSTM32RecoverFromBusOff()` being a no-op on F7 is correct. ABOM handles the full
recovery cycle in hardware including clearing ESR.BOFF. No software action is required or
appropriate.

---

## Evidence

### 1. ABOM behavior — RM0410 §40.9.2, CAN_MCR Bit 6

> **Bit 6 ABOM: Automatic bus-off management**
> This bit controls the behavior of the CAN hardware on leaving the Bus-Off state.
>
> **0:** The Bus-Off state is left on software request, once 128 occurrences of 11 recessive
> bits have been monitored and the software has first **set and cleared the INRQ bit** of the
> CAN_MCR register.
>
> **1:** The Bus-Off state is left **automatically by hardware** once 128 occurrences of 11
> recessive bits have been monitored.

The ABOM=0 description reveals the mechanism: cycling INRQ (init → normal) is what
exits bus-off and clears BOFF. With ABOM=1, hardware performs that INRQ cycle
automatically.

### 2. Bus-Off recovery sequence — RM0410 §40.7.6

> Depending on the ABOM bit in the CAN_MCR register, bxCAN recovers from Bus-Off
> (become error active again) either automatically or on software request. But in both cases
> the bxCAN has to wait at least for the recovery sequence specified in the CAN standard
> (128 occurrences of 11 consecutive recessive bits monitored on CANRX).
>
> If ABOM is set, the bxCAN starts the recovering sequence automatically after it has
> entered Bus-Off state.

"Become error active again" = the node exits bus-off state completely. BOFF is a status
flag reflecting bus-off state; when the state is left, BOFF clears.

### 3. ESR.BOFF flag — RM0410 §40.9.2, CAN_ESR Bit 2

> **Bit 2 BOFF: Bus-off flag**
> This bit is set by hardware when it enters the bus-off state. The bus-off state is entered
> on TEC overflow, greater than 255.

Access type: `r` (read-only). Software cannot clear it — hardware manages it as a pure
status flag. It reflects the current bus-off condition.

### 4. HAL source confirmation — stm32f7xx_hal_can.c:2038

```c
/* Check Bus-off Flag */
if (((interrupts & CAN_IT_BUSOFF) != 0U) &&
    ((esrflags & CAN_ESR_BOFF) != 0U))
{
    /* Set CAN error code to Bus-Off */
    errorcode |= HAL_CAN_ERROR_BOF;

    /* No need for clear of Error Bus-Off as read-only */
}
```

ST's own HAL explicitly documents that BOFF requires no software clearing — hardware
manages it.

---

## Why the Previous Fix Attempt Failed

The `HAL_CAN_Stop/Start` approach caused a full FC lockup because:

1. It was **unnecessary** — ABOM=1 already handles recovery automatically
2. It was **unsafe** — called from scheduler context with CAN RX ISR active, creating a
   race condition where `HAL_CAN_Stop` set INRQ=1 (entering init mode) while the ISR
   was still running, corrupting peripheral state

The revert of that fix (`7e5e00c0c`) was correct.

---

## Current Driver State

`canardSTM32CAN1_Init()` configures: `hcan1.Init.AutoBusOff = ENABLE`

This sets CAN_MCR.ABOM=1. With this configuration:
1. Bus-off entry (TEC > 255): hardware sets ESR.BOFF, halts TX/RX
2. Hardware immediately begins monitoring for 128×11 recessive bits
3. After recovery sequence completes: hardware cycles INRQ automatically, ESR.BOFF
   clears, TEC resets, node returns to Error Active state
4. `canardSTM32GetProtocolStatus()` will read BusOff=false on next poll
5. State machine in `dronecan.c` transitions back to normal from BUS_OFF state

No gap exists. The recovery is fully automatic and complete.

---

## Recommendation

- **Close `investigate-f7-busoff-lock`** — no implementation required
- **No code changes needed** in `canard_stm32f7xx_driver.c`
- The no-op comment in `canardSTM32RecoverFromBusOff()` should be updated to explain
  WHY it is a no-op (ABOM handles it), so future developers don't repeat this investigation

Suggested comment update:

```c
void canardSTM32RecoverFromBusOff(void) {
    // No-op: AutoBusOff (ABOM=1) handles the full recovery sequence in hardware.
    // After 128×11 recessive bits, hardware cycles INRQ automatically and clears
    // ESR.BOFF. Software intervention is neither required nor safe here.
    // See RM0410 §40.7.6, §40.9.2 CAN_MCR.ABOM and CAN_ESR.BOFF.
}
```

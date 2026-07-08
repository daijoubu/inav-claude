# Advisory: Investigate FC CAN TX Stall in ERROR_ACTIVE/ERROR_PASSIVE

**Date:** 2026-05-18 06:55
**From:** Developer
**To:** Manager
**Type:** Advisory — New Project Request

## Summary

The H7 FDCAN controller appears to stop transmitting frames while still in ERROR_ACTIVE or ERROR_PASSIVE state (TEC < 255, not BUS_OFF). This is unexpected — CAN controllers should be able to transmit in all states up to BUS_OFF.

## Background

During overnight DroneCAN failure testing, we observed:

1. GNSS module (node 75) goes silent for ~3s periods (all message types stop simultaneously)
2. FC (node 1) accumulates TX errors (TEC=168, REC=0) because GNSS module isn't ACKing
3. When GNSS module recovers, the FC fails to immediately resume normal TX
4. FC NodeStatus frames continue at 1Hz but higher-rate FC TX (e.g., arming-related messages) appears suppressed

The FC's FDCAN is configured with `AutoRetransmission = DISABLE` (single-shot TX). Under CAN 2.0 spec, even with single-shot TX, the controller should continue attempting TX in ERROR_ACTIVE and ERROR_PASSIVE states. Only BUS_OFF should stop TX.

## Hypothesis

The H7 FDCAN peripheral may inhibit TX when the controller enters ERROR_PASSIVE and AutoRetransmission is disabled. Or there may be a race condition where the TX FIFO fills with unacknowledged messages and is never drained.

## Recommended Investigation

- Verify H7 FDCAN behavior in ERROR_PASSIVE with `AutoRetransmission = DISABLE`
- Check if TX FIFO fills and stops accepting new messages during error passive
- Verify if enabling `AutoRetransmission` prevents the stall
- Consider adding error interrupt handlers to capture protocol-level events
- Consider periodic TX FIFO purge/unstick mechanism during error recovery

## Related Files

- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c`
- `src/main/drivers/dronecan/dronecan.c`
- `src/main/drivers/dronecan/libcanard/canard_stm32_driver.h`

---
**Developer**

# Advisory: Investigate AP_Periph TX Buffer Overflow on GNSS Module

**Date:** 2026-05-18 06:55
**From:** Developer
**To:** Manager
**Type:** Advisory — New Project Request

## Summary

The GNSS module (MatekL431 running AP_Periph) exhibits intermittent CAN TX failures where ALL message types stop simultaneously for ~3s periods. This matches AP_Periph issue #29738 (multiframe message TX buffer overflow, still unfixed).

## Evidence

- 2.6hr candump: 140 min of perfect 25Hz GNSSFix → sudden triple gap sequence at end
- All 5 message types on node 75 drop simultaneously (GNSSFix, 0x0427, 0x0425, 0x4E23, NodeStatus)
- Gap pattern: intervals creep from 20ms → 200ms → 500ms → 1s → total silence 2.5-3s, repeated 3 times
- Pattern matches CAN controller ErrorPassive → BusOff → auto-recovery retry cycle
- Earlier short runs show zero gaps — only appears after extended continuous operation

## Suspected Root Cause

AP_Periph issue #29738: "DroneCAN Multiframe Message Drops" — when the AP_Periph TX buffer overflows, messages are silently dropped. Under repeated arm/disarm cycles with servo stress, the TX buffer accumulates multiframe messages that cannot be transmitted fast enough, eventually overflowing and corrupting the entire TX path. This causes the CAN controller to enter ERROR_PASSIVE/BUS_OFF.

## Recommended Investigation

- Confirm AP_Periph firmware version on MatekL431 GNSS module
- Test with latest AP_Periph 4.7.0-beta5 (known to include some CAN fixes)
- Check if reducing multiframe message traffic reduces gap frequency
- Consider reporting to ArduPilot with our candump logs as evidence
- Evaluate if GNSS module can be configured to reduce TX message rate

## Related

- AP_Periph upstream issue: https://github.com/ArduPilot/ardupilot/issues/29738
- Current stable: AP_Periph 1.8.0 (2025-06-03)
- Current beta: AP_Periph 4.7.0-beta5

---
**Developer**

# Todo: Fix GPS Capability Poll 500ms Stall

## Phase 1: Implement Fix

- [ ] Read current code in `gps_ublox.c` gpsProtocolStateThread main loop (~lines 1227-1240)
- [ ] Read initial setup code (~lines 1200-1212) to confirm the correct wait pattern
- [ ] Fix MON-GNSS poll wait: use `gpsState.lastCapaUpdMs` timestamp change instead of ACK/NAK
- [ ] Fix MON-VER poll wait: use `gpsState.hwVersion != UBX_HW_VERSION_UNKNOWN` instead of ACK/NAK
- [ ] Verify no other MON-class polls have the same ACK/NAK wait bug

## Phase 2: Verify & Submit

- [ ] SITL build compiles cleanly
- [ ] PR created against `maintenance-9.x`
- [ ] Reference PR #11322 and breadoven's finding in PR description
- [ ] Send completion report to manager

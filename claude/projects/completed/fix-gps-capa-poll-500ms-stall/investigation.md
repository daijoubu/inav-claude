# GPS Capability Poll 500ms Stall Bug

## Summary
Every 5 seconds, `gpsProcessNewSolutionData` is not called for 500ms due to a bug in the capability polling logic in the main GPS loop.

## Location
`inav/src/main/io/gps_ublox.c` lines 1227-1240 (inside `gpsProtocolStateThread`)

## Root Cause
`pollGnssCapabilities()` sends UBX-MON-GNSS (a MON-class poll). The u-blox protocol only sends ACK/NAK for CFG-class messages, never for MON-class polls. But lines 1234 and 1238 wait on `_ack_state == UBX_ACK_GOT_ACK || _ack_state == UBX_ACK_GOT_NAK`, a condition that will **never** become true for MON messages. This causes `ptWaitTimeout` to always hit the full 500ms (`GPS_CFG_CMD_TIMEOUT_MS`) timeout.

Same issue applies to `pollVersion()` (UBX-MON-VER) at line 1233.

## Impact
- State thread blocks for 500ms (or 1000ms if hwVersion unknown) every 5 seconds
- `gpsProcessNewSolutionData` not called during the stall
- At 10 Hz GPS, ~5 position fixes go unprocessed each cycle
- Affects all u-blox M8+ modules with autoConfig enabled

## Fix Approach
Wait on the **response data arriving** instead of ACK/NAK. The initial setup code already does this correctly at lines 1208-1212:
```c
ptWaitTimeout((ubx_capabilities.capMaxGnss != 0), GPS_CFG_CMD_TIMEOUT_MS);
```

For the main loop:
- **Line 1238 (MON-GNSS):** Wait on a timestamp change, e.g. `gpsState.lastCapaUpdMs` changing (set at line 731 when MON-GNSS response is parsed)
- **Line 1234 (MON-VER):** Wait on `gpsState.hwVersion != UBX_HW_VERSION_UNKNOWN` (same as initial setup at line 1200)

## Key Constants
- `GPS_CAPA_INTERVAL` = 5000ms (gps_ublox.h:40)
- `GPS_CFG_CMD_TIMEOUT_MS` = 500ms (gps_ublox.h:32)

## Related Code
- `ubx_capabilities` struct: line 113-118
- `pollGnssCapabilities()`: line 256-262
- `pollVersion()`: line 248-254
- MON-GNSS response handler: line 724-733 (sets `gpsState.lastCapaUpdMs`)
- ACK handler: line 775-783 (only triggers for ACK/NAK message types)
- `sendConfigMessageUBLOX()`: line 233-246 (sets `_ack_state = UBX_ACK_WAITING`)

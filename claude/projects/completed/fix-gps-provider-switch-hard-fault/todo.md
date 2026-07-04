# Todo: GPS Provider Switch Hard Fault Fix

## Phase 1: Reproduce & Confirm Root Cause

- [ ] Reproduce the bug: boot with `gps_provider = MSP` or `FAKE`, then `set gps_provider = UBLOX` via CLI without reboot
- [ ] Confirm hard fault occurs on next scheduler tick via `gpsUpdate()` → `serialRxBytesWaiting(NULL)`
- [ ] Identify exact lines in `gps.c` and `gps_private.h` to change

## Phase 2: Implementation

- [ ] Add `initProvider` field to gpsState (in `gps_private.h`) — record provider at `gpsInit()` time
- [ ] In `gpsUpdate()`: compare `gpsConfig()->provider` against `initProvider`
- [ ] On mismatch: close serial port if open, call `gpsInit()`, return early
- [ ] Confirm no double-init or resource leak on normal boot path

## Phase 3: Verify

- [ ] CLI provider switch from MSP/FAKE → UBLOX no longer hard faults
- [ ] Normal GPS init (provider unchanged) still works
- [ ] Build matrix: F4, F7, H7, AT32, SITL — all pass

## Completion

- [ ] Code compiles on full build matrix
- [ ] PR opened against `release/9.1` (NOT maintenance-10.x, NOT master)
- [ ] GitHub issue referenced in PR description
- [ ] Completion report sent to manager

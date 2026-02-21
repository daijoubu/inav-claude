# Project: Test NEXUS DSM Verification

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Testing / Verification
**Created:** 2026-02-21
**Estimated Effort:** 2-4 hours

## Overview

Verify that DSM (Spektrum satellite receiver) functionality works correctly on the NEXUS target from PR #11324. The target has a dedicated DSM port on UART1 (PA9/PA10) with 3.3V power, but defaults to CRSF on UART4.

## Problem

PR #11324 adds the NEXUS target with DSM port hardware support, but:
- Default receiver is CRSF on UART4, not DSM
- No explicit DSM testing has been performed
- Need to verify DSM works when user configures it

## Objectives

1. Verify DSM serial RX works on UART1
2. Document configuration steps for DSM users
3. Optionally add SPEKTRUM_BIND_PIN if hardware supports it

## Test Scope

**In Scope:**
- DSM protocol detection on UART1
- SPEKTRUM1024 and SPEKTRUM2048 modes
- Satellite receiver binding (if bind pin available)
- Channel mapping verification

**Out of Scope:**
- Changing default receiver from CRSF
- Other receiver protocols (SBUS, IBUS, etc.)

## Hardware Required

- RadioMaster Nexus (Original) flight controller
- Spektrum satellite receiver (DSM2 or DSMX)
- Spektrum-compatible transmitter for binding

## Test Procedure

1. **Build NEXUS firmware** from PR #11324 branch
2. **Flash to hardware** via DFU
3. **Configure DSM:**
   ```
   serial 0 64 115200 57600 0 115200   # UART1 for serial RX
   set serialrx_provider = SPEKTRUM2048
   save
   ```
4. **Connect satellite receiver** to DSM port
5. **Bind receiver** to transmitter
6. **Verify in Configurator:**
   - Receiver tab shows channel values
   - Channels respond to transmitter input
   - No signal loss or glitches

## Success Criteria

- [ ] DSM satellite detected on UART1
- [ ] Channel values display in Configurator
- [ ] Transmitter inputs map correctly
- [ ] No signal stability issues
- [ ] Configuration steps documented

## Related

- **PR:** [iNavFlight/inav#11324](https://github.com/iNavFlight/inav/pull/11324)
- **Parent Project:** test-pr-11324 (completed)
- **Target:** NEXUS (RadioMaster Nexus Original)

## Notes

- DSM port provides 3.3V / 0.5A power (sufficient for satellite)
- UART1 pins: TX=PA9, RX=PA10
- If bind pin exists on hardware, consider adding SPEKTRUM_BIND_PIN define

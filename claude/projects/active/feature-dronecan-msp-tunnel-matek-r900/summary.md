# Project: MSP Tunneling over DroneCAN for Matek R900-30C mLRS Receiver

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Feature
**Created:** 2026-08-09
**Estimated Time:** 5-10 hours

## Overview

Implement MSP tunneling over DroneCAN using the `uavcan.tunnel.*` messages
(`Broadcast`, `Targetted`, `Protocol` — already DSDL-generated under
`lib/main/Dronecan/dsdlc_generated/`) so MSP/MSPv2 traffic can be relayed
to/from CAN-attached devices. Nothing in `src/main` currently uses these
generated types — this is new integration work, not a fix to existing code.

## Problem

mLRS supports MSP/MSPv2 and RC control over the air. The Matek R900-30C is
an mLRS receiver that connects via DroneCAN rather than a UART, so its MSP
interface (used for configuration/telemetry, e.g. via Configurator or the
`query_setting_info.py`-style MSP tooling) is currently unreachable — there's
no path from INAV's MSP layer onto the CAN bus.

## Objectives

1. Implement a DroneCAN tunnel client/relay in the DroneCAN driver using
   `uavcan.tunnel.Broadcast` (and/or `Targetted`) messages.
2. Bridge tunneled MSP payloads to/from an INAV MSP endpoint (e.g. a virtual
   MSP port, or relay through existing MSP serial/command dispatch in
   `src/main/msp/`) so Configurator or CLI-level MSP tooling can reach the
   receiver.
3. Verify against real R900-30C hardware — confirm the receiver's MSP
   responses tunnel correctly in both directions.

## Scope

**In Scope:**
- `uavcan.tunnel.*` message handling in the DroneCAN driver
- MSP payload bridging to/from an addressable endpoint
- Hardware verification with the R900-30C

**Out of Scope:**
- `sensors.rc.RCInput` RC channel decode (tracked separately in
  `feature-dronecan-rcinput`)
- Any mLRS-specific MSP message additions beyond standard MSP/MSPv2

## Related

`feature-dronecan-rcinput` — same receiver, independent DSDL message types,
no code dependency between the two projects, but the developer may want to
sequence/test them together given they share hardware (R900-30C).

## Success Criteria

- [ ] `tunnel.Broadcast`/`Targetted` messages correctly relay MSP
      requests/responses to/from a CAN node
- [ ] Verified against real Matek R900-30C hardware (e.g. via Configurator
      or an MSP query script)
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Estimated Time

5-10 hours

## Priority Justification

MEDIUM-HIGH: needed to configure/monitor the specific receiver hardware the
user is deploying, but RC control itself (tracked separately in
`feature-dronecan-rcinput`, HIGH priority) functions without this — this is
config/telemetry access on top of a link that already works.

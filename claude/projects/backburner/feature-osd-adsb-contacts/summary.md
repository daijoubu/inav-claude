# Project: OSD ADS-B Contact Display

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Time:** TBD — not yet scoped in detail

## Overview

Display ADS-B contacts on the INAV OSD, mirroring the existing INAV Radar contact display. Uses DroneCAN `ADSBVehicle` messages from external receivers (ADSBee, PingRX, FLARM).

## Problem

Pilots flying with a DroneCAN-connected ADS-B receiver have no way to see nearby manned/ADS-B-equipped traffic directly on the OSD — situational awareness for airspace conflicts currently requires a separate display or app.

## Objectives

1. Receive and parse DroneCAN `ADSBVehicle` messages
2. Render contacts on the OSD using the existing Radar contact display conventions (position, relative bearing/distance, altitude)

## Scope

**In Scope:**
- DroneCAN `ADSBVehicle` message handler
- OSD contact rendering, reusing INAV Radar's existing display patterns

**Out of Scope (until scoped further):**
- Non-DroneCAN ADS-B ingestion paths (e.g. direct UART receivers) — DroneCAN-only for now

## Success Criteria

- [ ] DroneCAN `ADSBVehicle` messages parsed and stored
- [ ] Contacts rendered on OSD, consistent with Radar display conventions
- [ ] Build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PR opened against `maintenance-10.x`

## Priority Justification

Useful safety feature for mixed airspace operations, but no active demand driving it — deprioritized behind higher-priority DroneCAN work.

## Dependencies

None known. Not yet assigned or discussed with developer beyond this outline — backfilled 2026-07-07 from the INDEX.md description to give this project actual doc files (previously just an empty directory).

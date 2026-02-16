# Project: OSD Display ADSB Contacts

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Effort:** 6-8 hours

## Overview

Add the ability for INAV OSD to display ADSB (Automatic Dependent Surveillance-Broadcast) contacts on the HUD in the same manner as INAV Radar contacts are displayed.

## Problem

INAV already supports displaying "INAV Radar" contacts (other aircraft using INAV with telemetry) on the OSD. However, there is no support for displaying ADSB contacts from external ADSB receivers (e.g., ADSBee, PingRX, FLARM devices). Users with ADSB hardware cannot see nearby traffic on their OSD.

## Objectives

1. Understand current INAV Radar display implementation
   - How radar contacts are stored and updated
   - How they are rendered on OSD

2. Add ADSB contact support parallel to INAV Radar
   - Create ADSB contact data structure
   - Add ADSB message handling (ADSBVehicle from DroneCAN/UAVCAN)
   - Integrate with position estimator for relative positioning

3. Add OSD elements for ADSB contacts
   - Display ADSB contacts similarly to INAV Radar
   - Show contact info (callsign, altitude, distance)
   - Support multiple contacts

## Scope

**In Scope:**
- ADSB contact data structure and management
- DroneCAN ADSB message handling
- OSD elements for ADSB display
- Integration with existing radar display system

**Out of Scope:**
- ADSB transmission (TX) functionality
- GUI configurator changes (CLI only)
- Integration with specific ADSB hardware beyond DroneCAN

## Implementation Steps

1. Research existing INAV Radar implementation
   - Find radar contact structures
   - Find OSD radar rendering code
   - Understand contact management

2. Create ADSB contact infrastructure
   - Define adsbContact_t or extend radarContact_t
   - Add DroneCAN ADSB message handler
   - Implement relative position calculation

3. Add OSD elements
   - Create ADSB OSD elements similar to radar
   - Implement contact rendering
   - Add OSD items to configurator

4. Test the implementation

## Success Criteria

- [ ] ADSB contacts received via DroneCAN are parsed correctly
- [ ] ADSB contacts displayed on OSD similar to INAV Radar
- [ ] Callsign, altitude difference, and distance shown
- [ ] Multiple ADSB contacts supported
- [ ] Backwards compatible (works without ADSB hardware)

## Related

- **INAV Radar:** Existing feature to reference
- **DroneCAN implementation:** PR #11313

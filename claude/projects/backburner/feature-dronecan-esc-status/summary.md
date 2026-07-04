# Project: DroneCAN ESC Status Telemetry

**Status:** ⏸️ BACKBURNER
**Priority:** HIGH
**Type:** Feature
**Created:** 2026-06-06
**Estimated Time:** 8-12 hours

## Overview

Add DroneCAN ESC Status telemetry support to receive motor/ESC health and performance data from DroneCAN ESCs via `uavcan.equipment.esc.Status`.

## Problem

INAV has no way to receive ESC health, temperature, RPM, or fault data from DroneCAN ESCs. Adding support would enable real-time ESC monitoring, fault detection, and richer telemetry to ground stations.

## Objectives

1. Subscribe to `uavcan.equipment.esc.Status` messages
2. Map ESC index to motor number
3. Expose data: RPM, voltage, current, temperature, error count
4. Feed into existing telemetry/OSD pipeline where applicable

## Scope

**In Scope:**
- DroneCAN ESC Status message reception (firmware)
- ESC index → motor mapping
- Exposure via MSP telemetry and/or OSD

**Out of Scope:**
- ESC configuration or parameter setting via DroneCAN
- Non-DroneCAN ESC telemetry

## Success Criteria

- [ ] ESC Status messages received and parsed
- [ ] Data mapped to correct motor indices
- [ ] Data exposed via telemetry (MSP) and/or OSD
- [ ] Full build matrix passes (F4/F7/H7/AT32/SITL)

## Priority Justification

HIGH — ESC health monitoring is valuable for in-flight fault detection. Parked on backburner until active queue clears.

## Reference

- daijoubu/inav #7
- ArduPilot DroneCAN ESC implementation for reference patterns

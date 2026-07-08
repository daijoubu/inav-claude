# Status Update: DroneCAN PR #11313 Collaboration - Phase 2 Complete

**Date:** 2026-02-11 09:22
**From:** Developer
**To:** Manager
**Re:** collaborate-dronecan-pr11313

## Current Status

Phase 2 (CAN Current Sensor) is COMPLETE. Moving to Phase 3 analysis.

## Progress Since Task Assignment

1. Cloned and reviewed daijoubu's add-libcanard branch
2. Analyzed the existing DroneCAN implementation structure
3. Found that BatteryInfo message ALREADY includes current data (pbatteryInfo->current)
4. The dronecanBattSensorGetAmperage() function existed but was NOT integrated with INAV's battery system
5. Implemented the missing integration:
   - Added CURRENT_SENSOR_CAN enum value
   - Added case handler in battery.c
   - Updated settings.yaml to expose CAN option for current_meter_type
6. Build passed (SITL target)
7. All 81 unit tests pass
8. Committed: f54bb4d4e "Add DroneCAN current sensor support to battery system"

## Discovery - Parameter Get/Set Protocol

Investigated the parameter protocol requirement. Findings:

- DSDL message definitions exist (GetSet_req.h, GetSet_res.h, etc.)
- NO implementation exists in dronecan.c
- This would be significant new work requiring:
  * Service request handlers for GetSet
  * Mapping DroneCAN parameter names to INAV settings
  * Integration with INAV's parameter group system
  * Testing with DroneCAN tools
- Estimated effort: 8-12 hours additional

## Blockers

None for current sensor work.

## Recommendation

Consider whether parameter get/set is essential for the initial PR, or if it can be deferred to a follow-up. The current implementation provides:

- GPS via DroneCAN
- Battery voltage via DroneCAN
- Battery current via DroneCAN (just added)

## Next Steps

1. Phase 3 (HITL Testing) - Requires hardware setup
2. Phase 4 (Documentation) - Can proceed with wiki docs for current functionality
3. Phase 5 (Parameter Protocol) - If approved, will implement

## Estimated Completion

- Current functionality: Ready for documentation
- Parameter protocol: Needs decision on scope

---
**Developer**

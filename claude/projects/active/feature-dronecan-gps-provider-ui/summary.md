# Project: Add DroneCAN GPS Provider Option to INAV Configurator UI

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature / UI Enhancement
**Created:** 2026-02-16
**Estimated Effort:** 8-12 hours

## Overview

Add support for selecting DroneCAN as a GPS provider in the INAV Configurator UI. Currently, the configurator allows users to select GPS providers (NONE, UBLOX, PAYLOAD, MSP, EXTERNAL, VIRTUAL), but DroneCAN is not exposed as an option, despite being supported by the firmware.

## Problem

With DroneCAN integration in INAV, flight controllers can now receive GPS data from DroneCAN devices (e.g., DroneCAN GPS modules). However:
1. The configurator UI doesn't expose DroneCAN as a GPS provider option
2. Users cannot easily enable/configure DroneCAN GPS without manual parameter editing
3. Inconsistent with other protocol support (MSP, UBLOX, etc.)

## Scope

### In Scope ✅
- Add DroneCAN to GPS provider dropdown in Configurator
- Update related UI elements
- Ensure proper setting value handling
- Add any necessary validation
- Update configurator documentation/tooltips
- Test GPS provider selection with DroneCAN

### Out of Scope ❌
- Firmware changes (GPS provider support already exists)
- Hardware-level testing
- DroneCAN module communication

## Solution Overview

### 1. Identify GPS Provider Setting Location
- Find where GPS provider setting is defined in configurator
- Identify the enumeration/options list
- Determine the firmware setting name and values

### 2. Add DroneCAN Option
- Add "DroneCAN" to GPS provider dropdown list
- Map correct firmware value for DroneCAN GPS provider
- Ensure enumeration values match firmware (gps_provider_e)

### 3. Update UI Components
- GPS configuration tab
- GPS provider selector/dropdown
- Related labels and tooltips
- Settings validation

### 4. Testing
- Verify DroneCAN option appears in dropdown
- Confirm selection persists
- Validate proper firmware value is set
- Test with actual firmware configuration

## Implementation Strategy

### Phase 1: Research (1-2 hours)
- Locate GPS provider setting definition in configurator
- Check firmware for DroneCAN GPS provider enum value
- Understand current provider options and structure
- Identify all UI components needing updates

### Phase 2: Implementation (4-6 hours)
- Add DroneCAN to provider list
- Update dropdown/selector UI
- Update validation logic
- Add any necessary constants/mappings
- Update tooltips and documentation strings

### Phase 3: Testing (2-3 hours)
- Functional testing of GPS provider selector
- Verify DroneCAN option displays correctly
- Test selection persistence
- Test with SITL/firmware verification
- User interface responsiveness testing

### Phase 4: Cleanup & Documentation (1-2 hours)
- Code review and polish
- Add comments where needed
- Update configurator documentation if applicable
- Prepare completion report

## Success Criteria

- [x] DroneCAN appears as option in GPS provider dropdown
- [x] User can select DroneCAN as GPS provider
- [x] Selection persists when saving configuration
- [x] Correct firmware setting value is set (matches firmware enum)
- [x] UI displays properly with new option
- [x] No regressions in other GPS provider options
- [x] Tooltips/help text updated appropriately
- [x] Tested with SITL or hardware validation

## Key Files to Investigate

**Configurator:**
- GPS settings/provider configuration UI
- Settings definitions and enumerations
- GPS configuration tab
- Provider dropdown/selector component
- Constants and setting value mappings

**Firmware Reference:**
- `src/main/fc/settings.yaml` - GPS provider setting definition
- GPS provider enumeration (gps_provider_e)
- MSP message handling for GPS configuration
- CLI implementation (for reference)

## Related Investigations

- **investigate-dronecan-sitl** - SITL testing with DroneCAN
- **dronecan-sitl-implementation** - DroneCAN SITL implementation
- **feature-dronecan-node-filter** - Previous DroneCAN UI feature

## Technical Notes

### Current GPS Providers (from firmware)
- NONE (0)
- UBLOX (1)
- PAYLOAD (2)
- MSP (3)
- EXTERNAL (4)
- VIRTUAL (5)
- DRONECAN (6) - ← **New option to expose**

### Firmware Setting
- Setting: `gps_provider`
- Type: uint8_t / enumeration
- Values: 0-6 (matches enum above)
- Persistence: EEPROM

### UI Location
- Configurator GPS tab
- GPS provider selector dropdown
- Should be alongside existing options (UBLOX, MSP, etc.)

## Dependencies

- INAV Configurator codebase
- Knowledge of Configurator settings system
- Understanding of GPS provider enum in firmware

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Enum value mismatch | Verify firmware enum matches added value |
| UI regression | Test all GPS provider options still work |
| Setting not persisting | Test with SITL and verify MSP communication |

## Questions for Implementation Team

1. Should DroneCAN GPS provider have any special validation/warning?
2. Are there any configurator platform differences (Electron vs Web) to consider?
3. Should GPS provider change trigger any other UI updates?
4. What additional help text is needed for DroneCAN GPS provider?

## Related Projects

- **code-review-maintenance-10-vs-libcanard** - Context on libcanard integration
- **investigate-msp-mavlink-dronecan-equivalents** - Protocol understanding
- **hitl-tests-add-libcanard-matekh743** - Testing context

## Notes

This is a straightforward feature addition that exposes existing firmware capability in the UI. The DroneCAN GPS provider is already supported by the firmware; this work focuses on making it user-accessible through the configurator.

**Impact:** Improves user experience by allowing easy DroneCAN GPS configuration without manual parameter editing.

---

**Project created:** 2026-02-16
**Owner:** Manager
**Assigned to:** Developer

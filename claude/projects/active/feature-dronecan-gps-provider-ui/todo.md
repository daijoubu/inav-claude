# Todo: Add DroneCAN GPS Provider to Configurator UI

## Phase 1: Research & Analysis

- [ ] Locate GPS provider setting in configurator source code
- [ ] Find GPS provider dropdown/selector component
- [ ] Check INAV firmware for DroneCAN GPS provider enum value
- [ ] Review current provider options and implementation pattern
- [ ] Document all files that need changes
- [ ] Identify configurator platform considerations (Electron/Web/Both)

## Phase 2: Implementation - Core Changes

- [ ] Add DroneCAN (value 6) to GPS provider enumeration
- [ ] Update GPS provider dropdown/selector list
- [ ] Add DroneCAN label and translation strings
- [ ] Update settings validation logic if needed
- [ ] Test basic selection in dropdown

## Phase 3: Implementation - UI Polish

- [ ] Add helpful tooltip for DroneCAN GPS provider
- [ ] Update any related documentation strings
- [ ] Verify UI layout with new option
- [ ] Check for any platform-specific issues
- [ ] Review styling/appearance consistency

## Phase 4: Testing

- [ ] Verify DroneCAN option displays in dropdown
- [ ] Test selecting DroneCAN GPS provider
- [ ] Verify selection persists after save
- [ ] Test switching between all GPS provider options
- [ ] Verify no regressions in other providers
- [ ] Test with SITL if possible
- [ ] Cross-browser/platform testing if applicable

## Phase 5: Final Cleanup

- [ ] Code review and refactoring
- [ ] Add inline comments where helpful
- [ ] Remove debug logging/temporary code
- [ ] Verify no console warnings/errors
- [ ] Final testing pass

## Completion Checklist

- [ ] All GPS providers work correctly
- [ ] DroneCAN is selectable and persistent
- [ ] No UI regressions
- [ ] Documentation updated
- [ ] Code clean and reviewed
- [ ] Test results documented
- [ ] Completion report submitted

---

## Notes

- Start with research phase to understand configurator structure
- Look for existing GPS provider implementation as reference
- Pay attention to value mappings (firmware enum → UI)
- Consider any validation needed for DroneCAN GPS provider

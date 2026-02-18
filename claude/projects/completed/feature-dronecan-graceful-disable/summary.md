# Project: Graceful DroneCAN Disable on CAN Bus Initialization Failure

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Feature / Reliability Enhancement
**Created:** 2026-02-16
**Completed:** 2026-02-16
**Actual Effort:** ~4-5 hours (faster than estimated 6-10 hours)
**PR:** [#TBD](https://github.com/daijoubu/inav) - Pending on add-libcanard branch

---

## Overview

Implement graceful disabling of DroneCAN subsystem when CAN bus hardware initialization fails. Currently, if CAN hardware initialization fails, DroneCAN may attempt operations on unavailable hardware, potentially causing undefined behavior. This project adds detection, logging, and safe fallback mechanisms to ensure system stability.

## Problem

**Scenario:**
- User has DroneCAN enabled (USE_DRONECAN defined)
- CAN hardware fails to initialize (loose connector, hardware defect, power issue)
- DroneCAN task continues running and attempts I/O on non-functional hardware
- System may hang, crash, or exhibit unpredictable behavior

**Current Behavior:**
- No detection of initialization failure
- No fallback mechanism
- User may be unaware the feature is non-functional
- Potential for safety-critical operations to fail silently

**Desired Behavior:**
- Detect CAN hardware initialization failure
- Log clear error message
- Gracefully disable DroneCAN and all dependent sensors
- Maintain system stability and continue other operations
- Allow operator to diagnose the issue via logs/blackbox

## Solution Overview

Implement graceful degradation pattern:
1. **Add initialization status tracking** in CAN driver layer
2. **Detect initialization failures** in dronecan.c initialization
3. **Disable DroneCAN task** if hardware unavailable
4. **Disable dependent sensors** (GPS, Battery from DroneCAN)
5. **Log detailed error information** for diagnostics
6. **Maintain system stability** (no crashes, flights possible without DroneCAN)

## Objectives

1. ✅ Add initialization status tracking to CAN/FDCAN HAL drivers
2. ✅ Implement failure detection in dronecan initialization
3. ✅ Gracefully disable DroneCAN task on init failure
4. ✅ Disable dependent sensors (GPS, Battery)
5. ✅ Add comprehensive logging/diagnostics
6. ✅ Test graceful degradation scenarios
7. ✅ Document failure modes and recovery procedures

## Implementation

### Phase 1: Hardware Driver Modifications
- Modify STM32 CAN HAL initialization to return status
- Add `dronecanInitStatus` tracking variable
- Implement initialization error detection
- Files: `canard_stm32f7xx_driver.c`, `canard_stm32h7xx_driver.c`, `canard_sitl_driver.c`

### Phase 2: DroneCAN Core Modifications
- Add `dronecanInitStatus` state variable
- Detect initialization failures in `dronecanInit()`
- Implement safe state (non-operational but not crashing)
- Add error logging with diagnostics
- Files: `dronecan.c`, `dronecan.h`

### Phase 3: Task Scheduling
- Conditionally disable TASK_DRONECAN if initialization failed
- Prevent task from running on non-functional hardware
- Alternative: Run task in degraded mode (safe check before operations)
- Files: `fc_tasks.c`

### Phase 4: Sensor Integration
- GPS DroneCAN: Check initialization before using data
- Battery DroneCAN: Check initialization before using data
- Fallback to other sensors if available
- Files: `io/gps_dronecan.c`, `sensors/battery_sensor_dronecan.c`

### Phase 5: Logging & Diagnostics
- Add DEBUG level logging of initialization status
- Log CAN peripheral errors
- Include in startup diagnostics
- Optional: Add to debug output screens
- Files: `dronecan.c`, affected drivers

### Phase 6: Testing & Documentation
- Test with CAN hardware disconnected
- Test with CAN initialization blocked
- Verify system stability and graceful degradation
- Test dependent sensors behavior
- Update documentation

## Success Criteria

- [ ] CAN initialization failures detected reliably
- [ ] DroneCAN cleanly disabled on init failure
- [ ] No system crashes or hangs on CAN init failure
- [ ] Clear error logging visible in debug output
- [ ] Other flight systems continue operating normally
- [ ] GPS and Battery from alternative sources work
- [ ] All tests passing
- [ ] Documentation updated

## Technical Considerations

### Error Detection Strategy
**Option A (Recommended):** Check init status at multiple points
- In dronecanInit()
- At task startup (defensive)
- Before critical operations

**Option B:** Fail-fast in initialization only
- Simpler, less overhead
- Less defensive, assumes init check sufficient

### State Management
- Add `dronecan_init_status_t` enum with states: UNINIT, INITIALIZING, OK, FAILED
- Use atomic flag to track status
- Safe for concurrent access (ISR + task)

### Task Behavior
- Option 1: Disable task entirely if init fails (cleanest)
- Option 2: Keep task running but with safety checks (more defensive)
- Recommended: Option 1 (cleaner, less overhead)

### Logging Strategy
- Use LOG_ERROR() for initialization failure
- Include HAL error codes if available
- Log at fc_init time for visibility

## Files to Modify

**Hardware Drivers:**
- `src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`
- `src/main/drivers/dronecan/libcanard/canard_stm32h7xx_driver.c`
- `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c`

**Core DroneCAN:**
- `src/main/drivers/dronecan/dronecan.c`
- `src/main/drivers/dronecan/dronecan.h`

**System Integration:**
- `src/main/fc/fc_init.c`
- `src/main/fc/fc_tasks.c`

**Sensor Integration:**
- `src/main/io/gps_dronecan.c`
- `src/main/sensors/battery_sensor_dronecan.c`

## Related Issues/PRs

- Code Review: [#11339](https://github.com/iNavFlight/inav/issues/11339) - Add libcanard recommendations
- Feature: DroneCAN integration (maintenance-10.x branch)

## Acceptance Criteria

### Development
- [ ] Code compiles without warnings
- [ ] All unit tests passing
- [ ] Integration test with simulated CAN init failure
- [ ] Code review approved
- [ ] Documentation complete

### Testing
- [ ] SITL test with CAN init failure scenario
- [ ] Hardware test with disconnected CAN
- [ ] Graceful degradation verified
- [ ] Logging output verified
- [ ] No memory leaks or resource leaks

### Documentation
- [ ] Code comments explain error handling
- [ ] Troubleshooting guide: "CAN bus initialization failed"
- [ ] Developer guide updated

## Estimated Timeline

- Phase 1 (Hardware): 1-2 hours
- Phase 2 (Core): 1.5-2 hours
- Phase 3 (Scheduling): 0.5-1 hour
- Phase 4 (Sensors): 1-1.5 hours
- Phase 5 (Logging): 0.5-1 hour
- Phase 6 (Testing): 2-3 hours
- **Total:** 6-10 hours

## Priority Justification

**MEDIUM Priority** because:
- Not blocking (workaround: check hardware before flight)
- Reliability improvement, not new feature
- Affects production deployment robustness
- Complements libcanard integration (recent addition)
- Relatively small scope, high impact on reliability

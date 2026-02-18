# Todo: Graceful DroneCAN Disable on CAN Bus Init Failure

## Phase 1: Hardware Driver Modifications (1-2 hours)

- [ ] Review STM32F7 CAN initialization in canard_stm32f7xx_driver.c
  - [ ] Identify initialization entry points
  - [ ] Check for error returns from HAL_CAN_Init()
  - [ ] Plan status tracking mechanism
- [ ] Modify STM32F7 driver
  - [ ] Add initialization status variable
  - [ ] Return status from init function
  - [ ] Add error logging
- [ ] Review and modify STM32H7 FDCAN driver (similar pattern)
  - [ ] Add initialization status variable
  - [ ] Return status from init function
- [ ] Review SITL driver initialization
  - [ ] Determine if SITL needs failure detection (stub mode fallback exists)
  - [ ] Ensure consistent status reporting
- [ ] Verify error detection logic
  - [ ] Test with simulated init failures

## Phase 2: DroneCAN Core Modifications (1.5-2 hours)

- [ ] Update dronecan.h
  - [ ] Add dronecan_init_status_t enum
  - [ ] Add status tracking variable declarations
  - [ ] Update function signatures if needed
- [ ] Modify dronecan.c initialization
  - [ ] Call hardware init functions
  - [ ] Check return status from HAL initialization
  - [ ] Set dronecanInitStatus based on results
  - [ ] Add error logging with hardware details
- [ ] Implement safe error state
  - [ ] Skip libcanard initialization if hardware failed
  - [ ] Prevent message processing
  - [ ] Document error state behavior
- [ ] Add state machine handling
  - [ ] Ensure STATE_DRONECAN_INIT properly detects failure
  - [ ] Transition to error state on init failure
  - [ ] Prevent transition to normal operation if hardware failed

## Phase 3: Task Scheduling (0.5-1 hour)

- [ ] Review fc_tasks.c DroneCAN task setup
  - [ ] Understand task registration mechanism
  - [ ] Identify where to add status check
- [ ] Implement conditional task disabling
  - [ ] Check dronecanInitStatus in fcTasksInit()
  - [ ] Don't enable TASK_DRONECAN if initialization failed
  - [ ] Log task disable reason
- [ ] Alternative: Implement task safety checks (if chosen)
  - [ ] Add guard in dronecanUpdateTask()
  - [ ] Return early if not initialized
- [ ] Verify task doesn't run on uninitialized hardware
  - [ ] Test task disable logic
  - [ ] Confirm no task execution occurs

## Phase 4: Sensor Integration (1-1.5 hours)

- [ ] Update GPS DroneCAN integration
  - [ ] Add check for dronecanInitStatus
  - [ ] Skip GPS processing if DroneCAN not initialized
  - [ ] GPS will fall back to other sources (serial, etc.)
- [ ] Update Battery sensor integration
  - [ ] Add check for dronecanInitStatus
  - [ ] Skip battery processing if DroneCAN not initialized
  - [ ] Battery will fall back to other sources if available
- [ ] Test sensor fallback behavior
  - [ ] Verify GPS works without DroneCAN
  - [ ] Verify battery monitoring without DroneCAN
  - [ ] Check graceful fallback to other sensors

## Phase 5: Logging & Diagnostics (0.5-1 hour)

- [ ] Add startup logging
  - [ ] Log "DroneCAN initialization: OK" on success
  - [ ] Log "DroneCAN initialization FAILED" on failure with error code
  - [ ] Include hardware-specific error details
- [ ] Add debug level logging
  - [ ] Log initialization steps (driver init, libcanard init, etc.)
  - [ ] Log final status at startup
- [ ] Update documentation
  - [ ] Document what errors look like in logs
  - [ ] Add troubleshooting: "CAN bus initialization failed"
  - [ ] Explain recovery steps (check hardware, restart)

## Phase 6: Testing & Validation (2-3 hours)

- [ ] Unit test initialization failure detection
  - [ ] Test STM32F7 init failure handling
  - [ ] Test STM32H7 init failure handling
  - [ ] Test SITL behavior
- [ ] SITL integration test
  - [ ] Build SITL with DroneCAN enabled
  - [ ] Simulate CAN init failure (mock HAL to return error)
  - [ ] Verify graceful degradation
  - [ ] Verify logging output
  - [ ] Verify task not running
- [ ] Hardware integration test (if available)
  - [ ] Disconnect CAN hardware
  - [ ] Boot flight controller
  - [ ] Verify graceful disable in logs
  - [ ] Verify other systems work
- [ ] Verify no memory leaks
  - [ ] Check for proper cleanup on init failure
  - [ ] Verify no dangling allocations
- [ ] Performance test
  - [ ] Ensure failure detection doesn't impact normal operation
  - [ ] Verify minimal overhead

## Completion

- [ ] All code compiles without warnings
- [ ] All tests passing (unit + integration)
- [ ] Code review complete
- [ ] Documentation updated
- [ ] PR created and ready for merge
- [ ] Completion report sent to manager

---

## Notes for Developer

**Start with:** Phase 1 - Review current hardware initialization to understand error handling patterns

**Key Decision Point:** Phase 3 - Decide between:
- Option A: Disable task entirely (recommended - cleaner)
- Option B: Keep task with safety checks (more defensive)

**Testing Strategy:**
- Start with SITL (easier to simulate failures)
- Then hardware if available
- Test both graceful disable path and normal operation path

**Documentation Focus:**
- Clear error messages in logs
- Troubleshooting guide for users who see initialization failures
- Code comments explaining the graceful degradation pattern

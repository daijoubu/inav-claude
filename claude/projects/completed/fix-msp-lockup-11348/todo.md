# Todo: Fix MSP Lock-up Issue #11348

## Phase 1: Critical Fixes (FIX #1 + #2)

### FIX #1: serialIsConnected() Return Statement
- [ ] Create git branch from investigation/issue-11348-msp-lockup
- [ ] Open `src/main/drivers/serial.c` line 111-118
- [ ] Add `return` statement to `serialIsConnected()` function
- [ ] Verify change (1 line modified)
- [ ] Compile firmware (check for warnings)
- [ ] Test basic connectivity detection

### FIX #2: Timeout in waitForSerialPortToFinishTransmitting()
- [ ] Open `src/main/io/serial.c` line 505-510
- [ ] Add timeout mechanism (millis-based)
- [ ] Add break condition when timeout exceeded
- [ ] Verify change (~5 lines)
- [ ] Compile firmware (check for warnings)
- [ ] Test with disconnected ports

### Phase 1 Verification
- [ ] Build firmware with LOG_DEBUG enabled
- [ ] Connect to MATEK F405 via USB
- [ ] Reproduce disconnection scenario (should not freeze anymore)
- [ ] Verify motors respond after reconnection

---

## Phase 2: Secondary Fixes (FIX #3 + #4)

### FIX #3: Timeout in printf.c
- [ ] Open `src/main/common/printf.c` line 229
- [ ] Add timeout mechanism to busy-wait loop
- [ ] Update line 288 with same pattern
- [ ] Verify changes (~3 lines)
- [ ] Compile firmware (check for warnings)

### FIX #4: Connection Check in log.c
- [ ] Open `src/main/common/log.c` line 140-141
- [ ] Add `serialIsConnected()` check before sending LOG messages
- [ ] Verify change (1 line modified)
- [ ] Compile firmware (check for warnings)
- [ ] Test LOG output with disconnected ports

### Phase 2 Verification
- [ ] Build firmware with all 4 fixes
- [ ] Test LOG_DEBUG output with port disconnections
- [ ] Verify printf output doesn't cause issues
- [ ] Test rapid connect/disconnect cycles

---

## Phase 3: Testing & Validation

### Hardware Testing (MATEK F405)
- [ ] Obtain MATEK F405 board for testing
- [ ] Flash firmware with all fixes
- [ ] Test disconnection scenario (USB cable pull)
- [ ] Test rapid connect/disconnect (10+ cycles)
- [ ] Verify firmware stability and responsiveness

### SITL Testing
- [ ] Build SITL firmware
- [ ] Run existing serial communication tests
- [ ] Run LOG_DEBUG tests
- [ ] Run rapid port change tests
- [ ] Verify all tests pass

### H7/F7 Board Testing (CONFIRMED - Both affected)
- [x] Developer confirmed H7 and F7 boards are affected by same bugs
- [ ] Test on F7-based board with same scenarios
- [ ] Test on H7-based board with same scenarios
- [ ] Document F7/H7 board behavior

### Integration Testing
- [ ] Run full configurator + firmware integration tests
- [ ] Test LOG_DEBUG with various debug topics
- [ ] Test with multiple rapid connects/disconnects
- [ ] Test with network-based connections (if applicable)

---

## Phase 4: Code Review & PR

### Code Review
- [ ] Use inav-code-review agent to review all changes
- [ ] Verify fixes follow coding standards
- [ ] Check for any unintended side effects
- [ ] Ensure error handling is robust
- [ ] Review timeout values (100ms appropriate?)

### Pull Request
- [ ] Create comprehensive PR description
- [ ] Reference issue #11348
- [ ] Include testing results
- [ ] Include before/after behavior description
- [ ] Note fixes for all 4 bugs
- [ ] Add to release notes

### Merge Readiness
- [ ] All CI checks pass
- [ ] Code review approved
- [ ] Hardware testing verified
- [ ] Documentation updated (if needed)

---

## Completion Checklist

### Code Changes
- [ ] FIX #1: serialIsConnected() return statement (1 line)
- [ ] FIX #2: timeout in waitForSerialPortToFinishTransmitting() (5 lines)
- [ ] FIX #3: timeout in printf.c (3 lines)
- [ ] FIX #4: connection check in log.c (1 line)

### Testing
- [ ] SITL tests pass
- [ ] Hardware test on MATEK F405 passes
- [ ] Reproduction test confirms fix
- [ ] Rapid disconnect/reconnect test passes

### Documentation
- [ ] Code comments updated (if needed)
- [ ] Issue #11348 resolution documented
- [ ] Release notes updated
- [ ] Investigation branch preserved for reference

### Final Steps
- [ ] All tests passing
- [ ] PR merged to maintenance-9.x
- [ ] Completion report sent to manager
- [ ] Original assignment archived
- [ ] Lock file released

---

## Notes

- **Reference:** Investigation findings in `investigate-msp-lockup-11348/` project
- **Investigation Branch:** `investigate/issue-11348-msp-lockup` (contains exact code locations)
- **Key Files:**
  - `src/main/drivers/serial.c` (FIX #1)
  - `src/main/io/serial.c` (FIX #2)
  - `src/main/common/printf.c` (FIX #3)
  - `src/main/common/log.c` (FIX #4)
- **Test Scenario:** Disconnect MSP reader while LOG_DEBUG is active
- **Expected Result:** Firmware continues running, no lock-up

---

**Created:** 2026-02-20
**Type:** Bug Fix (4 interconnected bugs)
**Severity:** CRITICAL
**Base Branch:** maintenance-9.x

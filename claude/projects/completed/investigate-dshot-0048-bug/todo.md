# TODO: DShot 0048 Bug Investigation

**Issue:** #10648 - DShot sending 0048 on forward after reverse
**Status:** Not Started
**Estimated Time:** 6-9 hours (includes ESC firmware verification + KISS telemetry investigation)

---

## Phase 0: ESC Firmware Verification (2-3h) ⚠️ **DO THIS FIRST**

**Critical:** Before fixing, verify our understanding of DShot 3D protocol against actual ESC firmware.

### Part 1: DShot 3D Protocol Verification (1-2h)

- [ ] **Review Bluejay ESC Firmware**
  - Repository: https://github.com/bird-sanctuary/bluejay
  - Find DShot value interpretation code
  - Confirm: Is 48 min reverse or max reverse?
  - Confirm: Is 1047 max reverse or min reverse?
  - Document findings

- [ ] **Review AM32 ESC Firmware**
  - Repository: https://github.com/AlkaMotors/AM32-MultiRotor-ESC-firmware
  - Find DShot value interpretation code
  - Confirm same questions as Bluejay
  - Check for consistency with Bluejay

- [ ] **Document DShot Protocol Results**
  - Create: `claude/developer/investigations/dshot-3d-protocol-verification/`
  - Summary of ESC firmware behavior
  - Confirm or refute our assumptions:
    - 48-1047 = reverse range
    - 1048-2047 = forward range
    - 48 = minimum reverse (stick just below center)
    - 1047 = maximum reverse (stick at bottom)

**If assumptions are WRONG, STOP and reassess the entire bug analysis!**

### Part 2: KISS Telemetry Investigation (+1h)

**Context:** INAV has known issues with KISS telemetry on AM32 ESCs, but works fine with Bluejay.

- [ ] **Locate KISS Telemetry in Bluejay**
  - Find UART telemetry / KISS protocol implementation
  - Document packet format and structure
  - Note timing characteristics (update rate, baud rate)
  - Extract code snippets

- [ ] **Locate KISS Telemetry in AM32**
  - Find UART telemetry / KISS protocol implementation
  - Document packet format and structure
  - Note timing characteristics
  - Extract code snippets

- [ ] **Compare Implementations**
  - Identify differences in packet format
  - Identify differences in timing
  - Identify differences in data fields
  - Note any non-standard behavior in AM32
  - Document potential INAV compatibility issues

- [ ] **Document KISS Telemetry Findings**
  - Add section to verification document
  - List all differences found
  - Analyze which differences could cause INAV issues
  - Recommend INAV code changes if needed

---

## Phase 1: Code Investigation (2-3h)

### 1.1 Locate DShot Mixer Code
- [ ] Find mixer code for rover platform
  - `inav/src/main/flight/mixer.c`
  - Rover-specific mixer functions
  - DShot value calculation

- [ ] Find bidirectional DShot handling
  - Search for "bidirectional" in mixer code
  - Reverse throttle range handling (48-1047)
  - Forward throttle range handling (1048-2047)

- [ ] Trace value calculation path
  - From RC input → mixer → DShot output
  - Identify where 1000 offset applied for forward
  - Identify where reverse offset applied

### 1.2 Identify Bug Location
- [ ] Find state machine for direction handling
  - How reverse mode is entered/exited
  - How neutral transitions are handled
  - State clearing on neutral

- [ ] Analyze value calculation
  - Check if 0048 could be from (1048 - 1000) calculation error
  - Verify offset application order
  - Look for integer overflow/underflow

- [ ] Review recent changes
  - Git history for mixer changes
  - Git history for bidirectional DShot changes
  - Check if bug introduced recently or long-standing

---

## Phase 2: Reproduction (1-2h)

### 2.1 SITL Setup
- [ ] Configure SITL as rover
  - Set platform to rover
  - Enable bidirectional DShot
  - Configure motor outputs

- [ ] Prepare monitoring
  - Add debug output for DShot values
  - Set up logging for mixer calculations
  - Prepare to capture exact sequence

### 2.2 Reproduce Bug
- [ ] Follow exact reproduction sequence
  ```
  1. Arm (neutral)
  2. Forward throttle
  3. Back to neutral
  4. Reverse throttle
  5. Back to neutral
  6. Forward throttle ← CAPTURE VALUE HERE
  ```

- [ ] Verify 0048 appears
  - Confirm bug exists in current master
  - Document exact conditions
  - Note any additional triggers

- [ ] Test variations
  - Try different throttle amounts
  - Try different timing
  - Try rapid direction changes

---

## Phase 3: Fix Development (1-2h)

### 3.1 Develop Fix
- [ ] Implement solution (choose based on root cause):

  **Option A: Clear reverse state on neutral**
  ```c
  if (rcCommand[THROTTLE] == neutral) {
      reverseMode = false;
      // Clear any reverse offsets
  }
  ```

  **Option B: Fix offset calculation**
  ```c
  // Ensure forward always uses 1048+ range
  if (direction == FORWARD) {
      dshotValue = 1048 + throttleAmount;
  } else if (direction == REVERSE) {
      dshotValue = 48 + throttleAmount;
  }
  ```

  **Option C: Add boundary check**
  ```c
  // Prevent invalid values
  if (dshotValue > 47 && dshotValue < 1048) {
      // Force to correct range
      if (intendedDirection == FORWARD) {
          dshotValue += 1000;
      }
  }
  ```

- [ ] Add comments explaining fix
- [ ] Ensure no side effects

### 3.2 Code Review
- [ ] Check similar code paths
  - Other platforms using bidirectional DShot
  - Ensure fix doesn't break airplane/multirotor
  - Verify VTOL compatibility

- [ ] Review against DShot spec
  - Confirm value ranges correct
  - Verify command values not affected
  - Check special command handling

---

## Phase 4: Testing (1h)

### 4.1 Unit Testing
- [ ] Test fix in SITL
  - Verify original bug is gone
  - Test forward-neutral-forward (should still work)
  - Test reverse-neutral-forward (should now be correct)
  - Test reverse-neutral-reverse
  - Test rapid direction changes

- [ ] Edge case testing
  - Very short neutral periods
  - Partial throttle amounts
  - Zero throttle vs actual neutral
  - Throttle cut vs disarm

### 4.2 Regression Testing
- [ ] Verify no new bugs introduced
  - Test airplane mixer (should be unchanged)
  - Test multirotor mixer (should be unchanged)
  - Test VTOL mixer (should be unchanged)
  - Test regular (non-bidirectional) DShot

### 4.3 Hardware Testing (if available)
- [ ] Test on actual rover with bidirectional DShot
  - Verify 0048 no longer appears
  - Verify smooth transitions
  - Verify no motor stuttering
  - Check ESC behavior

---

## Phase 5: Documentation & PR (30min)

### 5.1 Document Fix
- [ ] Write clear commit message
  - Describe bug (0048 sent instead of 1048+)
  - Explain root cause
  - Describe fix
  - Reference issue #10648

- [ ] Update this project summary
  - Document root cause found
  - Note fix implemented
  - Add test results

### 5.2 Create Pull Request
- [ ] Prepare PR
  - Clear title: "Fix DShot 0048 bug on reverse-to-forward transition"
  - Link to issue: "Fixes #10648"
  - Include test results
  - Request review from DShot experts

- [ ] Respond to review feedback
- [ ] Merge when approved

---

## Acceptance Criteria

✅ Fix complete when:
- Root cause identified and documented
- Fix implemented and tested in SITL
- No regression in other mixer types
- PR created and merged
- Issue #10648 closed

---

## Notes

- Focus on rover mixer specifically (don't break other platforms)
- Value 0048 is **boundary** between special commands (0-47) and reverse range (48-1047)
- Forward range is 1048-2047 (offset by +1000 from reverse)
- The fact that 0048 appears suggests offset not applied or removed incorrectly

---

## Time Tracking

| Task | Estimated | Actual |
|------|-----------|--------|
| Code Investigation | 2-3h | - |
| Reproduction | 1-2h | - |
| Fix Development | 1-2h | - |
| Testing | 1h | - |
| Documentation & PR | 30min | - |
| **Total** | **4-6h** | - |

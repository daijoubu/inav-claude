# Todo List: Fix JavaScript Programming Decompiler Warning

## Phase 1: Setup & Reproduction

- [ ] Load the provided CLI diff into SITL
- [ ] Navigate to JavaScript Programming tab
- [ ] Verify decompiler shows the warning
- [ ] Take screenshots documenting current behavior
- [ ] Document exact warning message and conditions

## Phase 2: Code Investigation

- [ ] Locate decompiler code in inav-configurator
  - [ ] Find programming tab implementation
  - [ ] Locate decompiler function
  - [ ] Identify validation logic
- [ ] Find operation type definitions
  - [ ] Locate operation 42 (Set Control Profile)
  - [ ] Document all operation types
  - [ ] Understand operation parameter requirements
- [ ] Trace validation flow
  - [ ] Find where "Invalid PID operand" warning is generated
  - [ ] Identify which code path is triggered
  - [ ] Understand why wrong validation is applied

## Phase 3: Root Cause Analysis

- [ ] Analyze operation 42 handling
  - [ ] What are valid operand values for Set Control Profile?
  - [ ] What does operand A represent? (appears to be profile number: 0)
  - [ ] What does operand B represent? (appears to be 1700)
- [ ] Understand the 1700 value
  - [ ] Is it used or ignored?
  - [ ] Is it a leftover from another operation?
  - [ ] Is it supposed to be validated?
- [ ] Identify validation bug
  - [ ] Why is PID validation applied to non-PID operation?
  - [ ] Is there missing operation-specific validation?
  - [ ] Is the validation lookup using wrong key?
- [ ] Document findings
  - [ ] Root cause summary
  - [ ] Expected vs actual behavior
  - [ ] Proposed fix approach

## Phase 4: Fix Implementation

- [ ] Fix validation logic
  - [ ] Ensure each operation uses correct validation rules
  - [ ] Add or fix Set Control Profile validation
  - [ ] Make warning messages operation-specific
- [ ] Handle operand B for Set Control Profile
  - [ ] Determine if 1700 should be validated
  - [ ] Determine if 1700 should be in decompiled output
  - [ ] Fix handling based on specification
- [ ] Update warning messages
  - [ ] Make warnings operation-specific
  - [ ] Ensure helpful error messages
  - [ ] Remove misleading "PID" references for non-PID ops

## Phase 5: Testing

- [ ] Test original case (Set Control Profile)
  - [ ] Load logic condition: `logic 0 1 -1 42 0 0 6 1700 0`
  - [ ] Verify no incorrect warning
  - [ ] Verify decompiled code is correct
- [ ] Test PID operations (regression check)
  - [ ] Ensure PID validation still works
  - [ ] Test with valid PID values
  - [ ] Test with invalid PID values (should warn)
- [ ] Test other override operations
  - [ ] Test Set VTX Power
  - [ ] Test Set OSD Layout
  - [ ] Test other override types
- [ ] Test various operand types
  - [ ] Different operand type/value combinations
  - [ ] Edge cases and boundary values

## Phase 6: Documentation

- [ ] Update code comments
  - [ ] Document validation logic
  - [ ] Explain operation-specific rules
- [ ] Document fix in commit message
  - [ ] Describe the bug
  - [ ] Explain root cause
  - [ ] Describe the solution
  - [ ] List test cases

## Phase 7: PR Creation

- [ ] Build configurator successfully
- [ ] Test in development mode
- [ ] Create PR targeting maintenance-9.x
- [ ] Include in PR description:
  - [ ] Bug description with screenshots
  - [ ] Root cause explanation
  - [ ] Fix description
  - [ ] Test cases performed
  - [ ] Before/after comparison
- [ ] Reference this project in PR

## Completion

- [ ] Code compiles successfully
- [ ] All tests passing
- [ ] No regressions identified
- [ ] PR created and submitted
- [ ] Send completion report to manager

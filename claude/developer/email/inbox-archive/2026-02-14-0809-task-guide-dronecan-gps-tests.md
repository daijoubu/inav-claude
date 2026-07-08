# Task Assignment: Guide Through DroneCAN HITL GPS Tests

**Date:** 2026-02-14 08:09
**From:** Manager
**To:** Developer
**Project:** dronecan-hitl-gps-tests
**Priority:** HIGH
**Estimated Effort:** 2-4 hours (depending on user availability)

## Task

Guide the user (robs) through completing the previously skipped GPS-related HITL tests now that they have a DroneCAN GPS module. Unlike a normal task where you do the work yourself, this time you will GUIDE/WALK THE USER through each test, prompting them on what to do at each step and tracking completion.

## Background

The user now has a DroneCAN GPS module and wants to complete the GPS-related tests that were previously skipped in the HITL test execution. The previous test session (hitl-test-execution-dronecan) had 8 GPS tests skipped due to no hardware availability.

## Reference Documents

- **Previous Test Results:** `claude/projects/completed/hitl-test-execution-dronecan/TEST-RESULTS.md`
- **Test Todo/List:** `claude/projects/active/dronecan-hitl-gps-tests/todo.md`
- **Project Directory:** `claude/projects/active/dronecan-hitl-gps-tests/`

## Skipped GPS Tests from Previous Session

The following tests need to be executed:

**Phase 1: Basic Validation**
- TEST-GPS-001: GPS Device Discovery
- TEST-GPS-002: Position Data Reception

**Phase 2: Functional Testing**
- TEST-GPS-003: Velocity Data Reception
- TEST-GPS-004: Fix Quality Reporting
- TEST-INT-001: GPS + Battery Simultaneous

**Phase 3: Robustness Testing**
- TEST-GPS-006: GPS Loss and Recovery
- TEST-INT-004: Hot Plug - GPS

**Phase 4: Stress Testing**
- TEST-GPS-005: GPS Fix2 Message Support
- TEST-GPS-007: GPS Data Update Rate

## What to Do

This is a guided testing task - you will NOT run tests yourself. Instead:

### 1. Start with Phase 1: Basic Validation
- Prompt the user to power on their GPS module
- Ask them to verify GPS discovery
- Have them check position data reception
- Track each test result

### 2. Progress Through Each Phase Sequentially
- Phase 2: Functional Testing
- Phase 3: Robustness Testing
- Phase 4: Stress Testing

### 3. For Each Test:
- Tell the user exactly what to do
- Wait for their response
- Record PASS/FAIL/SKIP for each test
- If FAIL, help troubleshoot and document the issue

### 4. Communication Approach
- Use the email system to send prompts to the user
- Track each test result in the email thread
- Be specific with instructions (e.g., "Check INAV Configurator GPS status - what satellite count do you see?")
- Wait for user response before proceeding to next test

### 5. After All Tests Complete
- Update the TEST-RESULTS.md file with new results (in `claude/projects/completed/hitl-test-execution-dronecan/`)
- Send completion summary to manager

## Success Criteria

- [ ] All 9 GPS-related tests executed with PASS/FAIL/SKIP status recorded
- [ ] TEST-RESULTS.md updated with new results
- [ ] Any issues found are documented
- [ ] Completion report sent to manager

## Important Notes

- Base branch: `maintenance-9.x` (INAV firmware)
- The user will be performing the actual hardware tests
- Your role is to guide, prompt, and track
- Be specific with instructions - the user needs clear direction on what to do at each step

---

**Manager**

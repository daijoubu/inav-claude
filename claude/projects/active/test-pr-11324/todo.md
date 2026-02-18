# Todo: Test PR #11324

## Phase 1: PR Analysis

- [ ] Review PR on GitHub
  - [ ] Read PR description and objectives
  - [ ] Review PR author's explanation
  - [ ] Check related issues and discussions

- [ ] Analyze changes
  - [ ] Identify files modified
  - [ ] Understand functional changes
  - [ ] Identify affected subsystems
  - [ ] Determine testing requirements

- [ ] Review existing tests
  - [ ] Check if related tests exist
  - [ ] Identify test gaps
  - [ ] Plan additional test cases

- [ ] Document testing strategy
  - [ ] Define test scope
  - [ ] List test cases to execute
  - [ ] Identify hardware targets (if needed)
  - [ ] Plan timeline

## Phase 2: SITL Testing

- [ ] Build SITL with PR changes
  - [ ] Checkout PR branch
  - [ ] Build SITL firmware
  - [ ] Verify build succeeds without warnings/errors

- [ ] Functional testing
  - [ ] Execute basic functionality tests
  - [ ] Test primary use cases from PR
  - [ ] Test secondary use cases
  - [ ] Test configuration options

- [ ] Edge case testing
  - [ ] Test boundary conditions
  - [ ] Test error handling
  - [ ] Test recovery scenarios
  - [ ] Test with invalid inputs

- [ ] Performance testing
  - [ ] Measure CPU usage
  - [ ] Check memory usage
  - [ ] Verify real-time performance
  - [ ] Document performance impact

- [ ] Regression testing
  - [ ] Test unrelated functionality
  - [ ] Run existing test suite
  - [ ] Verify no regressions found

## Phase 3: Hardware Testing (if applicable)

- [ ] Prepare hardware
  - [ ] Select appropriate targets
  - [ ] Flash with PR firmware
  - [ ] Verify hardware functionality

- [ ] Execute hardware tests
  - [ ] Run functional tests on hardware
  - [ ] Verify expected behavior
  - [ ] Test with real sensors
  - [ ] Document any hardware-specific issues

- [ ] Performance monitoring
  - [ ] Monitor CPU load
  - [ ] Check memory usage
  - [ ] Verify real-time performance
  - [ ] Document findings

## Phase 4: Regression Testing

- [ ] Verify core functionality
  - [ ] GPS/Navigation
  - [ ] Motor control
  - [ ] Attitude estimation
  - [ ] Configuration

- [ ] Test multiple configurations
  - [ ] Different flight modes
  - [ ] Different hardware targets
  - [ ] Different sensor configurations

- [ ] Documentation check
  - [ ] Verify documentation updates included
  - [ ] Check for incomplete documentation
  - [ ] Verify wiki references if needed

## Phase 5: Reporting

- [ ] Create test report
  - [ ] Document test environment (SITL/hardware)
  - [ ] List all test cases executed
  - [ ] Document results (pass/fail)
  - [ ] Include any issues found

- [ ] Report findings
  - [ ] Create GitHub comment on PR with test results
  - [ ] Include performance metrics
  - [ ] Note any bugs or regressions
  - [ ] Provide recommendations

- [ ] Follow-up
  - [ ] Create issues for any bugs found
  - [ ] Track feedback from PR author
  - [ ] Close project when PR is resolved

## Completion

- [ ] All test phases complete
- [ ] Test report created
- [ ] Feedback provided to PR author
- [ ] Follow-up issues created (if needed)
- [ ] Completion report sent to manager

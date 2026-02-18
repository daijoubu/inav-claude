# Todo: Finalize libcanard DroneCAN Integration

## Phase 1: Unit Tests for Message Decoders

- [ ] Set up test framework integration
  - [ ] Create test file structure
  - [ ] Configure test runner and CI integration
  - [ ] Add to INAV build system

- [ ] Test GPS message decoders
  - [ ] Test GNSS Fix decoding
  - [ ] Test GNSS Fix2 decoding
  - [ ] Test GNSS Auxiliary (satellite count, HDOP)
  - [ ] Test error cases and edge conditions
  - [ ] Test coordinate conversions and unit handling

- [ ] Test Battery sensor decoders
  - [ ] Test battery status message decoding
  - [ ] Test voltage and current parsing
  - [ ] Test state-of-charge calculations
  - [ ] Test error conditions

- [ ] Test other message handlers
  - [ ] NodeStatus monitoring
  - [ ] RTCM stream handling
  - [ ] Message queue edge cases
  - [ ] Buffer overflow conditions

- [ ] Coverage validation
  - [ ] Measure decoder coverage
  - [ ] Identify uncovered paths
  - [ ] Add tests for uncovered cases

## Phase 2: DroneCAN Configuration Documentation

- [ ] Review existing documentation in add-libcanard branch
  - [ ] Review docs/DroneCan.md for content and completeness
  - [ ] Review docs/DroneCan-Driver.md for technical details
  - [ ] Identify gaps and incomplete sections
  - [ ] Note any conflicts or redundancies
  - [ ] Extract reusable content for configuration reference

- [ ] Create/Update configuration reference
  - [ ] Document all configuration parameters
  - [ ] Explain each parameter's purpose and valid ranges
  - [ ] Document defaults and recommended values
  - [ ] Add CAN baudrate options
  - [ ] Integrate content from existing docs

- [ ] Create/Update feature documentation
  - [ ] Document USE_DRONECAN feature flag
  - [ ] Document platform-specific options
  - [ ] Document hardware compatibility
  - [ ] Document building with DroneCAN support
  - [ ] Consolidate with existing documentation

- [ ] Create troubleshooting guide
  - [ ] Common initialization issues
  - [ ] Bus error recovery
  - [ ] Message decode failures
  - [ ] Performance issues
  - [ ] Debugging techniques

- [ ] Add to INAV wiki
  - [ ] Create DroneCAN documentation page
  - [ ] Link from main GPS/Battery documentation
  - [ ] Add to configurator help

## Phase 3: Example Configurations

- [ ] Basic GPS example
  - [ ] Configuration steps
  - [ ] Expected behavior
  - [ ] How to verify

- [ ] Battery monitoring example
  - [ ] Configuration steps
  - [ ] Battery voltage/current setup
  - [ ] Verification steps

- [ ] Combined GPS + Battery example
  - [ ] Full configuration walkthrough
  - [ ] Multiple node setup
  - [ ] Verification checklist

- [ ] Multi-node DroneCAN setup
  - [ ] Node ID allocation
  - [ ] Dynamic node discovery
  - [ ] Example with multiple sensors

- [ ] SITL simulation examples
  - [ ] Running SITL with DroneCAN support
  - [ ] Simulating GPS messages
  - [ ] Simulating battery updates
  - [ ] Testing recovery scenarios

- [ ] Hardware-specific examples
  - [ ] STM32F745 setup
  - [ ] STM32H743 setup
  - [ ] Other target configurations
  - [ ] Baud rate and CAN options

## Quality Assurance

- [ ] All tests pass on SITL
- [ ] All tests pass on hardware targets
- [ ] Documentation reviewed for accuracy
- [ ] Examples tested end-to-end
- [ ] No regressions in existing functionality
- [ ] CI/CD validation passes

## Completion

- [ ] All unit tests complete and passing
- [ ] Configuration documentation complete
- [ ] Example configurations documented
- [ ] Code review recommendations marked complete
- [ ] PR created and linked
- [ ] Completion report sent to manager

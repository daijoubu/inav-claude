# Todo: HITL Tests for add-libcanard on MATEKH743

## Phase 1: Build & Setup

- [ ] Checkout add-libcanard branch
- [ ] Verify branch state and recent commits
- [ ] Build firmware for MATEKH743
  - [ ] Check firmware size vs available flash
  - [ ] Verify no build warnings/errors
- [ ] Setup HITL test environment
  - [ ] Configure SITL simulator
  - [ ] Setup DroneCAN test harness
  - [ ] Prepare GPS/Battery/ESC simulators

## Phase 2: Basic Functionality Tests

- [ ] HITL basic flight test
  - [ ] Arm/disarm
  - [ ] Throttle control
  - [ ] Basic navigation
- [ ] DroneCAN initialization
  - [ ] Node discovery
  - [ ] Message parsing
- [ ] GPS message reception
  - [ ] Verify position updates
  - [ ] Check fix quality
- [ ] Battery status updates
  - [ ] Voltage/current reception
  - [ ] Alert thresholds
- [ ] ESC telemetry
  - [ ] RPM reception
  - [ ] Temperature monitoring

## Phase 3: DroneCAN Feature Tests

- [ ] NodeStatus messages
  - [ ] Status broadcast
  - [ ] Health state transitions
- [ ] GetTransportStats requests
  - [ ] Request/response cycle
  - [ ] Stats accuracy
- [ ] Error condition handling
  - [ ] Corrupted frame handling
  - [ ] Timeout recovery
  - [ ] Bus off detection
- [ ] Multi-node communication
  - [ ] Multiple nodes on bus
  - [ ] Message arbitration
- [ ] Message filtering
  - [ ] Dynamic filtering
  - [ ] Performance impact

## Phase 4: Performance & Stability

- [ ] CPU usage monitoring
  - [ ] Baseline measurement
  - [ ] Peak vs average
- [ ] Memory usage patterns
  - [ ] Heap usage
  - [ ] Stack usage
- [ ] DroneCAN throughput
  - [ ] Message rate
  - [ ] Latency
- [ ] 60-minute stability run
  - [ ] No watchdog resets
  - [ ] No hardfaults
  - [ ] No message drops
- [ ] Drop/corruption rate
  - [ ] Calculate statistics
  - [ ] Identify patterns

## Phase 5: Documentation

- [ ] Collect all test results
- [ ] Create TEST-RESULTS.md
  - [ ] Test execution log
  - [ ] Pass/fail summary
  - [ ] Metrics table
- [ ] Document any issues found
- [ ] Performance metrics summary
- [ ] Recommendations for improvements

## Completion

- [ ] All tests executed
- [ ] Results documented
- [ ] Issues captured
- [ ] Report generated
- [ ] Send completion report to manager

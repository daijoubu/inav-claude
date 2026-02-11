# Todo List: Generate Test Code for DroneCAN/Libcanard

## Phase 1: Setup and Planning (1-2 hours)

- [ ] Checkout and build add-libcanard branch
- [ ] Review PR #11313 description and comments
- [ ] Identify test framework/infrastructure to use
- [ ] Create test directory structure
- [ ] Document test plan and approach

## Phase 2: Unit Tests - CAN Driver (3-4 hours)

- [ ] Test CAN driver initialization (STM32F7)
  - [ ] Valid configuration
  - [ ] Invalid parameters
  - [ ] Hardware initialization
- [ ] Test CAN driver initialization (STM32H7)
  - [ ] Valid configuration
  - [ ] Invalid parameters
  - [ ] Hardware initialization
- [ ] Test frame transmission
  - [ ] Standard ID frames
  - [ ] Extended ID frames
  - [ ] Data frames
  - [ ] Remote frames
- [ ] Test frame reception
  - [ ] Filter configuration
  - [ ] Frame matching
  - [ ] Buffer management
- [ ] Test error handling
  - [ ] Bus-off state
  - [ ] Error counters
  - [ ] Recovery procedures

## Phase 3: Unit Tests - Message Encoding/Decoding (3-4 hours)

- [ ] Test GPS Fix2 message
  - [ ] Encode valid GPS data
  - [ ] Decode valid message
  - [ ] Handle invalid data
  - [ ] Boundary conditions
- [ ] Test BatteryInfo message
  - [ ] Encode battery data
  - [ ] Decode battery message
  - [ ] Handle edge cases (0V, max voltage)
  - [ ] Temperature and capacity fields
- [ ] Test NodeStatus message
  - [ ] Encode node health
  - [ ] Decode status
  - [ ] Health codes
  - [ ] Uptime tracking
- [ ] Test GetNodeInfo request/response
  - [ ] Request encoding
  - [ ] Response decoding
  - [ ] Hardware/software version
  - [ ] Node name

## Phase 4: Unit Tests - Libcanard API (2-3 hours)

- [ ] Test memory pool management
  - [ ] Allocation
  - [ ] Deallocation
  - [ ] Out of memory handling
- [ ] Test transfer transmission
  - [ ] Single-frame transfers
  - [ ] Multi-frame transfers
  - [ ] Transfer ID sequencing
- [ ] Test transfer reception
  - [ ] Frame reassembly
  - [ ] Timeout handling
  - [ ] Duplicate detection
- [ ] Test CRC validation
  - [ ] Valid CRC
  - [ ] Invalid CRC
  - [ ] CRC computation

## Phase 5: Integration Tests - GPS DroneCAN (3-4 hours)

- [ ] Create test infrastructure
  - [ ] Python script to inject DroneCAN messages into SITL
  - [ ] MSP commands to read GPS data
  - [ ] Test harness setup
- [ ] Test GPS Fix2 message reception
  - [ ] SITL receives GPS coordinates
  - [ ] Position updates in INAV
  - [ ] GPS status reported correctly
- [ ] Test GPS data validation
  - [ ] Valid coordinates
  - [ ] Invalid coordinates (rejection)
  - [ ] GPS fix quality
  - [ ] Satellite count
- [ ] Test GPS timeout
  - [ ] Stop sending messages
  - [ ] GPS timeout detection
  - [ ] Failsafe behavior

## Phase 6: Integration Tests - Battery Sensor (2-3 hours)

- [ ] Test BatteryInfo message reception
  - [ ] SITL receives voltage/current
  - [ ] Battery data in INAV
  - [ ] Configurator display
- [ ] Test battery monitoring
  - [ ] Voltage thresholds
  - [ ] Current consumption
  - [ ] Capacity tracking
  - [ ] Low battery warnings
- [ ] Test battery sensor timeout
  - [ ] Stop sending messages
  - [ ] Timeout detection
  - [ ] Fallback behavior

## Phase 7: Integration Tests - Multi-Node (2-3 hours)

- [ ] Test multiple DroneCAN nodes
  - [ ] GPS + Battery sensor simultaneously
  - [ ] Node discovery
  - [ ] Message routing
- [ ] Test node enumeration
  - [ ] GetNodeInfo requests
  - [ ] Node database
  - [ ] Health monitoring
- [ ] Test bus management
  - [ ] Message prioritization
  - [ ] Bandwidth usage
  - [ ] Error handling with multiple nodes

## Phase 8: Documentation and Cleanup (1-2 hours)

- [ ] Document test setup
- [ ] Document how to run tests
- [ ] Document test coverage
- [ ] Create README for test directory
- [ ] Clean up test code
- [ ] Add comments and explanations

## Completion Checklist

- [ ] All unit tests written and passing
- [ ] All integration tests written and passing
- [ ] Tests documented
- [ ] Test infrastructure committed
- [ ] Send completion report to manager with:
  - [ ] Test coverage summary
  - [ ] How to run tests
  - [ ] Any issues found
  - [ ] Recommendations for PR reviewers

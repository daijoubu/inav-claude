# Todo: Collaborate on DroneCAN PR #11313

## Phase 1: Research & Setup

- [ ] Clone/fetch daijoubu's branch locally
- [ ] Review existing DroneCAN implementation in PR
- [ ] Understand libcanard library structure
- [ ] Identify existing patterns for sensors and protocols
- [ ] Review DroneCAN specification for current sensor and parameter messages

## Phase 2: CAN Current Sensor Driver

- [ ] Study existing battery voltage sensor implementation
- [ ] Identify DroneCAN message type for current sensing
- [ ] Implement current sensor driver following voltage sensor pattern
- [ ] Add unit tests for current sensor
- [ ] Test with SITL (simulated CAN messages)

## Phase 3: Parameter Get/Set Protocol

- [ ] Review DroneCAN parameter protocol specification
- [ ] Design integration with INAV settings system
- [ ] Implement parameter read (get) functionality
- [ ] Implement parameter write (set) functionality
- [ ] Add unit tests for parameter protocol
- [ ] Test parameter operations via SITL

## Phase 4: HITL Testing

- [ ] Set up HITL environment with CAN interface
- [ ] Test GPS driver with real/simulated GPS data
- [ ] Test battery voltage sensor
- [ ] Test current sensor (our contribution)
- [ ] Test parameter get/set
- [ ] Document test results and any issues found

## Phase 5: Documentation

- [ ] Write DroneCAN overview for wiki
- [ ] Document supported peripherals (GPS, battery, current)
- [ ] Document configuration options (bitrate, node ID)
- [ ] Add troubleshooting section
- [ ] Create wiring diagrams if applicable

## Completion

- [ ] All code compiles without warnings
- [ ] All unit tests pass
- [ ] HITL tests pass
- [ ] Documentation reviewed
- [ ] Submit contribution to PR author
- [ ] Send completion report to manager

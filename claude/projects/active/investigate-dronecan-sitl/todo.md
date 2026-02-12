# Todo: Investigate DroneCAN SITL Testing Support

## Phase 1: Research & Analysis

### Subtask 1.1: Understand Current State
- [ ] Map where dronecan module is used in firmware
- [ ] Identify conditional compilation that excludes SITL
- [ ] Document current SITL build configuration
- [ ] Find issue/PR discussions about DroneCAN and SITL

### Subtask 1.2: Analyze libcanard Architecture
- [ ] Study libcanard library structure
- [ ] Understand platform driver interface
- [ ] Document existing STM32F7/H7 driver implementations
- [ ] Identify what makes platform drivers platform-specific

### Subtask 1.3: Understand SITL Build Constraints
- [ ] Review cmake/sitl.cmake and build configuration
- [ ] Document SITL target platform (x86 Linux)
- [ ] Identify available SITL drivers/stubs
- [ ] Understand how other hardware modules handle SITL

## Phase 2: Evaluate Solutions

### Subtask 2.1: Stub/Mock Driver Option
- [ ] Document approach and architecture
- [ ] Pros and cons analysis
- [ ] Estimated effort to implement
- [ ] Testing capability assessment

### Subtask 2.2: Linux Native CAN Option
- [ ] Research SocketCAN API
- [ ] Assess complexity of implementation
- [ ] Pros and cons analysis
- [ ] Linux dependency implications

### Subtask 2.3: Virtual CAN Loop Option
- [ ] Design in-process CAN bus emulation
- [ ] Assess module compatibility
- [ ] Pros and cons analysis
- [ ] Estimated effort to implement

## Phase 3: Recommendation & Planning

### Subtask 3.1: Compare Solutions
- [ ] Create comparison matrix (effort, capability, maintainability)
- [ ] Identify blockers or dependencies for each approach
- [ ] Consider future expandability

### Subtask 3.2: Recommend Best Solution
- [ ] Document rationale for recommended approach
- [ ] Address trade-offs with alternatives
- [ ] Outline key implementation considerations

### Subtask 3.3: Create Implementation Plan
- [ ] Break down Phase 2 implementation into concrete tasks
- [ ] Identify files to modify/create
- [ ] Estimate effort and time
- [ ] Document success criteria for Phase 2

## Completion

- [ ] All research documented in project directory
- [ ] Recommendation document created
- [ ] Phase 2 implementation plan ready
- [ ] Completion report sent to manager

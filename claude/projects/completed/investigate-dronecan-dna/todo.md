# Todo: Investigate DroneCAN DNA Implementation

## Phase 1: Understand DNA Specification

- [ ] Research DroneCAN DNA protocol
  - [ ] Read DroneCAN specification for DNA
  - [ ] Identify DNA message types (Allocation, etc.)
  - [ ] Document state machine for node allocation
  - [ ] Note timing requirements

- [ ] Research libcanard DNA support
  - [ ] Check if libcanard has DNA implementation
  - [ ] Identify available functions/APIs
  - [ ] Document required setup

## Phase 2: Analyze Current Implementation

- [ ] Review current DroneCAN code
  - [ ] Review dronecan.c - node initialization
  - [ ] Review dronecan.h - public API
  - [ ] Identify current node ID handling

- [ ] Check existing DNA-related code
  - [ ] Search for "allocation" in codebase
  - [ ] Search for "dynamic_node_id" in DSDL files
  - [ ] Check if any DNA messages are handled

## Phase 3: Determine Implementation Requirements

- [ ] Identify required changes
  - [ ] What new messages need handling?
  - [ ] What changes to initialization?
  - [ ] What new data structures needed?

- [ ] Analyze UI implications
  - [ ] How does DNA affect configuration UI?
  - [ ] What settings are still needed?
  - [ ] How to display allocated node IDs?

## Phase 4: Create Implementation Plan

- [ ] Document architecture
  - [ ] Architecture diagram/text
  - [ ] Data flow for allocation
  - [ ] Integration with existing code

- [ ] Create step-by-step plan
  - [ ] Phase 1: Basic allocation client
  - [ ] Phase 2: Allocation server (if needed)
  - [ ] Phase 3: Integration testing

- [ ] Estimate timeline and risks
  - [ ] Effort estimate per phase
  - [ ] Potential blockers/risks
  - [ ] Mitigation strategies

## Phase 5: Document Findings

- [ ] Write investigation report
  - [ ] Executive summary
  - [ ] Technical analysis
  - [ ] Implementation plan
  - [ ] Risk assessment

- [ ] Submit to manager
  - [ ] Report in project directory
  - [ ] Send completion report

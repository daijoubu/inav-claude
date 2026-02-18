# Todo: MSP/Mavlink vs DroneCAN NodeStatus Investigation

## Phase 1: Understanding DroneCAN NodeStatus

- [ ] Locate DroneCAN NodeStatus message specification
- [ ] Document all fields in NodeStatus message with data types
- [ ] Create list of field purposes and use cases
- [ ] Identify mandatory vs optional fields

## Phase 2: MSP Protocol Research

- [ ] Search INAV codebase for MSP message definitions
- [ ] Identify all system/health-related MSP messages
  - [ ] MSP_STATUS
  - [ ] MSP_EXTENDED_STATUS
  - [ ] MSP_ANALOG
  - [ ] MSP_FC_VARIANT
  - [ ] Other relevant messages
- [ ] Document which fields map to DroneCAN NodeStatus
- [ ] Find MSP handler code in INAV

## Phase 3: Mavlink Protocol Research

- [ ] Research Mavlink message spec for node status
  - [ ] HEARTBEAT
  - [ ] SYS_STATUS
  - [ ] SYSTEM_TIME
  - [ ] Other relevant messages
- [ ] Identify Mavlink fields equivalent to DroneCAN NodeStatus
- [ ] Locate Mavlink integration in INAV

## Phase 4: INAV Source Code Analysis

- [ ] Find system health tracking in INAV
- [ ] Locate CPU/performance monitoring
- [ ] Find error counter aggregation
- [ ] Identify memory usage tracking
- [ ] Trace how each status field is calculated
- [ ] Document data sources and computation logic

## Phase 5: Ardupilot Comparison

- [ ] Research Ardupilot's NodeStatus implementation
- [ ] Compare field coverage vs INAV
- [ ] Identify differences in approach
- [ ] Document any best practices found

## Phase 6: Synthesis and Documentation

- [ ] Create comparison matrix/table
- [ ] Write gap analysis section
- [ ] Document findings clearly
- [ ] List recommendations for improvements
- [ ] Create visual diagrams if helpful

## Completion

- [ ] Investigation report written
- [ ] All findings documented
- [ ] Comparison matrices complete
- [ ] Recommendations provided
- [ ] Send completion report to manager

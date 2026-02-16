# Todo: Investigate DroneCAN Messages Roadmap

## Phase 1: Current State

- [x] List all DroneCAN messages currently supported by INAV
- [x] Note any partially implemented messages (like BatteryInfo SOC)
- [x] Document the current dronecan.c structure

## Phase 2: Message Survey

- [x] Review UAVCAN v0 DSDL message definitions
- [x] Identify sensor messages (equipment.*)
- [x] Identify actuator messages
- [x] Identify power/battery messages
- [x] Identify navigation messages
- [x] Identify system/protocol messages

## Phase 3: Evaluation

For each candidate message:
- [x] What functionality does it provide?
- [x] What peripherals commonly implement it?
- [x] How complex is implementation?
- [x] What user value does it add?

## Phase 4: Prioritization

- [x] Rank messages by priority (HIGH/MEDIUM/LOW)
- [x] Write justification for each ranking
- [x] Estimate implementation effort
- [x] Note any dependencies

## Completion

- [x] FINDINGS.md created with prioritized roadmap
- [ ] Report sent to manager

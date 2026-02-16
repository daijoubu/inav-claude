# Todo: Investigate CAN Driver Circular Buffer

## Phase 1: Find Implementations

- [x] Locate circular buffer in STM32F7 CAN driver
- [x] Locate INAV's common circular buffer library
- [x] Check for other circular buffer implementations in codebase

## Phase 2: Document Current CAN Buffer

- [x] Document buffer structure/typedef
- [x] Document API (init, push, pop, peek, full, empty)
- [x] Note thread safety mechanisms (volatile, critical sections)
- [x] Note element size handling

## Phase 3: Document Library Buffer

- [x] Document buffer structure/typedef
- [x] Document API
- [x] Check thread safety
- [x] Find existing usages in codebase

## Phase 4: Compare and Recommend

- [x] Create comparison table
- [x] Identify compatibility issues
- [x] Assess switching effort
- [x] Write recommendation with justification

## Completion

- [x] FINDINGS.md created with recommendation
- [ ] Report sent to manager

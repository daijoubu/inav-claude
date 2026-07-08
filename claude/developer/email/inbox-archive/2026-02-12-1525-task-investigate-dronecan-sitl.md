# Task Assignment: Investigate DroneCAN SITL Support

**Date:** 2026-02-12 15:25
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-sitl
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours
**Base Branch:** maintenance-9.x

## Task

Investigate how to enable DroneCAN testing in SITL. The DroneCAN module is currently excluded from SITL builds because libcanard only has drivers for STM32F7xx and STM32H7xx chips. This forces developers to use slower HITL testing with hardware.

## Background

DroneCAN is a critical subsystem for advanced flight control features, but the inability to test it in SITL creates a significant bottleneck:
- Developers must use slower HITL (hardware-in-the-loop) testing
- SITL testing is faster and more convenient for iterative development
- A solution would improve development velocity and reduce hardware dependencies

The challenge is that libcanard (the CAN abstraction library) only has platform drivers for specific STM32 hardware variants.

## What to Do

### Phase 1 - Research & Analysis

1. **Understand current state**
   - Where is DroneCAN currently used in the codebase
   - How is conditional compilation configured for SITL
   - Review SITL build configuration and constraints

2. **Analyze libcanard architecture**
   - Study the platform driver interface
   - Document existing STM32F7xx and STM32H7xx drivers
   - Understand how drivers are selected and compiled

3. **Understand SITL constraints**
   - What is the target platform for SITL builds
   - What CAN drivers are available in the environment
   - What are the architectural limitations

### Phase 2 - Evaluate Solutions

Research and evaluate at least 2-3 approaches:

1. **Stub/Mock driver approach**
   - Create a minimal mock CAN driver for SITL
   - Trade-offs: simple but limited functionality

2. **Linux native CAN (SocketCAN) approach**
   - Leverage Linux kernel CAN support
   - Trade-offs: requires kernel support, more realistic

3. **Virtual CAN loop approach**
   - Create an in-process virtual CAN bus
   - Trade-offs: self-contained, good for testing

### Phase 3 - Recommendation & Planning

1. Create a comparison matrix showing:
   - Implementation effort (hours)
   - Testing capability (mock vs realistic)
   - Maintainability
   - Integration complexity

2. Recommend the best solution with clear rationale

3. Create a detailed Phase 2 implementation plan with:
   - Specific code changes needed
   - Files to modify
   - Testing strategy
   - Effort estimate for implementation

## Success Criteria

- [x] Clear understanding of why DroneCAN is excluded from SITL
- [x] Documented libcanard architecture and driver interface
- [x] At least 2-3 solution approaches evaluated with detailed pros/cons
- [x] Recommended solution with implementation rationale
- [x] Detailed Phase 2 implementation plan with effort estimate
- [x] All findings documented in project files

## Files to Review

Start with these files in the project directory:
- `claude/projects/active/investigate-dronecan-sitl/summary.md` - Full project details
- `claude/projects/active/investigate-dronecan-sitl/todo.md` - Task breakdown

Then review relevant source code:
- `src/main/drivers/dronecan/` - DroneCAN module code
- `cmake/sitl.cmake` - SITL build configuration
- `src/platform/*/canbus_drivers.c` - Platform-specific CAN drivers

Repository: iNavFlight/inav (maintenance-9.x branch)

## Project Directory

`claude/projects/active/investigate-dronecan-sitl/`

All analysis, notes, and recommendations should be documented in the project files.

---
**Manager**

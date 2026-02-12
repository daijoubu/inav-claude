# Project: Investigate DroneCAN SITL Testing Support

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-12
**Estimated Effort:** 8-12 hours

---

## Overview

Investigate how to setup DroneCAN so the module can be tested in SITL. This will enable testing of follow-on modules to be tested in SITL as well.

---

## Problem

The DroneCAN module is conditionally excluded from SITL compilation because libcanard only has 2 platform-specific drivers for the STM32F7xx and STM32H7xx chips. This limits the amount of SITL testing that can be done, pushing the burden onto HITL which is slower and requires sample equipment.

**Key Issues:**
- DroneCAN module unavailable in SITL builds
- Only STM32F7xx and STM32H7xx libcanard drivers available
- SITL uses x86 Linux target - no platform support
- Forces developers to use HITL for DroneCAN testing
- HITL requires hardware and is slower for iteration

---

## Solution Approach

Investigate possible solutions to enable DroneCAN testing in SITL:

**Option 1: Stub/Mock Driver**
- Create a SITL-specific stub CAN driver
- Provides virtual CAN bus for testing module logic
- Pros: Minimal effort, good for unit testing
- Cons: Doesn't test actual CAN communication

**Option 2: Linux Native CAN Support**
- Implement libcanard driver for Linux native sockets
- Use SocketCAN (linux/can.h)
- Pros: Real CAN simulation, portable
- Cons: Requires Linux-specific code

**Option 3: Virtual CAN Loop**
- Implement in-process CAN bus emulation
- Direct callback-based message passing
- Pros: Fast, deterministic, no external dependencies
- Cons: Not true CAN protocol testing

---

## Objectives

1. **Research** - Analyze libcanard architecture and SITL build constraints
2. **Document** - Understand why current drivers are platform-specific
3. **Evaluate** - Assess pros/cons of each solution approach
4. **Recommend** - Propose best path forward for implementation
5. **Plan** - Create detailed implementation plan for approved solution

---

## Scope

**In Scope:**
- Understanding libcanard architecture
- Analyzing SITL build system and constraints
- Evaluating solution options
- Creating implementation plan

**Out of Scope:**
- Implementing the actual solution (Phase 2)
- Testing with actual DroneCAN devices
- Modifying libcanard library itself

---

## Success Criteria

- [ ] Clear understanding of why DroneCAN is excluded from SITL
- [ ] Documented architecture of libcanard drivers
- [ ] At least 2-3 solution approaches evaluated with pros/cons
- [ ] Recommended solution with detailed implementation plan
- [ ] Estimated effort and complexity for recommended solution
- [ ] Clear next steps for Phase 2 implementation

---

## Related

- **Repository:** iNavFlight/inav
- **Base Branch:** maintenance-9.x
- **Module:** src/main/drivers/dronecan/
- **Build System:** cmake/sitl.cmake

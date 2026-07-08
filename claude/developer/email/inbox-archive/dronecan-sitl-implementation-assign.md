# Task Assignment: DroneCAN SITL Implementation (Phase 2)

**To:** Developer
**From:** Manager
**Date:** 2026-02-12
**Subject:** Implement DroneCAN support in SITL - Phase 2 (16 hours)
**Status:** 📩 Sent

---

## Assignment

Based on successful completion of the Phase 1 investigation (investigate-dronecan-sitl), I'm assigning you **Phase 2: Implementation** of DroneCAN SITL support.

**Project:** `dronecan-sitl-implementation`
**Effort:** 16 hours total
**Priority:** MEDIUM

---

## Project Overview

Implement DroneCAN support in INAV SITL using a hybrid approach:

**Primary (Linux):** Real CAN protocol simulation via SocketCAN/vcan
- Actual CAN frames through kernel stack
- Multi-node capability for testing node discovery
- Works with external tools (candump, cansend)

**Fallback (macOS/Windows):** Stub driver for basic testing
- Graceful degradation on non-Linux platforms
- Foundation for future improvements

---

## Three Implementation Phases

### Phase 2.1: Stub Driver Foundation (4 hours)
Create minimal working SITL DroneCAN with stub driver.

**Files:**
- Create: `src/main/drivers/dronecan/libcanard/canard_sitl_driver.c`
- Modify: `dronecan.c`, `canard_stm32_driver.h`, `cmake/sitl.cmake`, `target/SITL/target.h`

### Phase 2.2: SocketCAN Integration (8 hours)
Implement real CAN communication via Linux SocketCAN API.

**Tasks:**
- SocketCAN socket management (create, bind, error handling)
- Non-blocking I/O with select()/poll()
- TX: Convert libcanard frames to CAN frames
- RX: Receive CAN frames and convert to libcanard format
- Interface name configuration (default: vcan0)
- Graceful fallback if socket unavailable

### Phase 2.3: Testing & Documentation (4 hours)
Verify functionality and update wiki.

**Tasks:**
- Create `scripts/test_dronecan_sitl.sh` test script
- Test single/multi-node scenarios
- Test with candump/cansend tools
- Update INAV wiki with vcan setup and testing procedures

---

## Success Criteria

- [x] Phase 1 investigation complete
- [ ] SITL compiles with USE_DRONECAN enabled
- [ ] DroneCAN task initializes and runs
- [ ] NodeStatus messages visible on vcan0
- [ ] Can inject/receive CAN frames via socket
- [ ] Two SITL instances can communicate
- [ ] Graceful fallback on non-Linux platforms
- [ ] Complete test suite and wiki documentation
- [ ] Code passes CI/CD checks

---

## Key Resources

All investigation phase research is available in:
`claude/developer/workspace/investigate-dronecan-sitl/`

**Files:**
- `RESEARCH-FINDINGS.md` - Architecture analysis
- `SOLUTION-OPTIONS.md` - Three options evaluation (detailed)
- `RECOMMENDATION.md` - Implementation plan with specific code examples

**Hybrid Recommendation Rationale:**
- SocketCAN provides real protocol testing and multi-node capability
- Linux is primary SITL platform (~95% of usage)
- Stub fallback provides graceful degradation for macOS/Windows

---

## Getting Started

1. **Use `/start-task dronecan-sitl-implementation`** to:
   - Verify clean working directory
   - Create feature branch from maintenance-9.x
   - Acquire project lock
   - Set up workspace

2. **Read the project files:**
   - `claude/projects/active/dronecan-sitl-implementation/summary.md`
   - `claude/projects/active/dronecan-sitl-implementation/todo.md`

3. **Follow the three phases in order:**
   - Phase 2.1 → 2.2 → 2.3 (don't skip phases)
   - Each phase builds on the previous

---

## Questions or Blockers?

Reply to this email or check:
- `RECOMMENDATION.md` - Detailed implementation guide
- `SOLUTION-OPTIONS.md` - Technical details on SocketCAN API
- `RESEARCH-FINDINGS.md` - DroneCAN architecture overview

---

## When Complete

Send a completion report including:
- Summary of implementation (3-4 sentences)
- Test results (which scenarios passed)
- Any deviations from the plan
- Wiki updates made

Use `/finish-task` to move project to completed/ and create PR.

---

**Expected Timeline:** 16 hours of focused work
**Next Assignment:** Available after completion

Good luck! This is a valuable feature that will help INAV developers test DroneCAN integration in SITL.


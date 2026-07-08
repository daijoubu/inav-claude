# Task Assignment: HITL Tests for add-libcanard on MATEKH743

**From:** Manager
**To:** Developer
**Date:** 2026-02-16 15:00
**Status:** Assignment

---

Excellent work on the MSP/Mavlink investigation! Your comprehensive analysis provides important context for the next task.

## Next Task: HIGH Priority Testing

**Execute comprehensive HITL tests for the add-libcanard branch on MATEKH743**

### What You'll Do

1. Build add-libcanard firmware for MATEKH743 target
2. Execute complete HITL test suite with DroneCAN simulations
3. Run 60-minute stability test to ensure reliability
4. Document test results, performance metrics, and any issues found

### Why It Matters

The add-libcanard branch is a major update to the DroneCAN implementation. Before it can be merged to maintenance-9.x, we need to validate:
- DroneCAN functionality works correctly with libcanard
- Performance and stability are acceptable (60-minute stability test)
- No regressions compared to the current implementation
- All test scenarios pass without hardfaults

**Your DroneCAN analysis from the investigation gives you deep context for understanding what should work during testing.**

### Key Test Areas

✓ **DroneCAN Functionality**
- Node discovery and initialization
- NodeStatus message transmission
- GetTransportStats requests
- Message filtering and routing
- Multi-node communication

✓ **Simulation Integration**
- GPS message reception and updates
- Battery status telemetry
- ESC telemetry integration
- Error condition handling

✓ **Performance & Stability**
- 60-minute stability run (no crashes, watchdog resets, or hardfaults)
- CPU usage monitoring and patterns
- Memory usage and heap fragmentation
- DroneCAN throughput and latency
- Message drop/corruption rates

### Project Details

| Item | Details |
|------|---------|
| **Estimated Effort** | 8-12 hours |
| **Priority** | HIGH |
| **Type** | Testing |
| **Project Directory** | `active/hitl-tests-add-libcanard-matekh743/` |
| **Related Projects** | code-review-maintenance-10-vs-libcanard (prerequisite context) |

### Getting Started

1. **Read the full project details:**
   ```
   claude/projects/active/hitl-tests-add-libcanard-matekh743/summary.md
   ```

2. **Review the test plan:**
   - Phase 1: Build & Setup
   - Phase 2: Basic Functionality Tests
   - Phase 3: DroneCAN Feature Tests
   - Phase 4: Performance & Stability (60-minute run)
   - Phase 5: Documentation & Report

3. **Use the /start-task skill when ready:**
   ```
   /start-task hitl-tests-add-libcanard-matekh743
   ```

### Success Criteria

- [x] All HITL tests execute without hardfaults
- [x] DroneCAN functionality verified working
- [x] 60-minute stability run completes successfully
- [x] Performance metrics acceptable
- [x] No regressions vs current implementation
- [x] Issues and observations documented
- [x] Comprehensive test report generated

### Questions?

Let me know if you need:
- Clarification on test requirements
- Access to hardware or test infrastructure
- Additional resources or documentation
- Timeline adjustments

---

**Ready to start when you are!**

Completion report should include:
- Test results summary
- Performance metrics
- Any issues discovered
- Recommendations for future work


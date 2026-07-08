# Guidance: Extend SD Card Test Script for HITL Testing

**Date:** 2026-02-23 10:45
**From:** Manager
**To:** Developer
**Re:** update-stm32f7-hal - Test Engineer Capability Extension

## Task

Continue working through the SD card test script to identify and develop modules that can extend the test-engineer capability for Hardware-In-The-Loop (HITL) testing.

## Objectives

1. **Audit existing test modules** - Review `sd-card-test-plan/` for reusable components
2. **Identify HITL-extendable modules** - Find tests that can be automated or parameterized
3. **Document integration points** - Note MSP commands, CLI hooks, and hardware interfaces that enable automated testing
4. **Propose test-engineer extensions** - Suggest modules that could become reusable HITL testing tools

## Focus Areas

- **Automated MSP queries** - Can test scripts query FC state without manual intervention?
- **ST-Link/GDB integration** - `debug_lockup.py` approach for automated state capture
- **Sensor simulation** - Can tests inject or mock sensor data?
- **Regression test suite** - Modules suitable for CI/CD integration

## Success Criteria

- [ ] Inventory of reusable test modules documented
- [ ] HITL integration points identified
- [ ] Recommendations for test-engineer tooling

## Related

- **Project:** `claude/projects/active/update-stm32f7-hal/`
- **Test Scripts:** `claude/developer/workspace/sd-card-test-plan/`
- **HITL Library:** `claude/developer/scripts/testing/hitl/__init__.py`
- **Branch:** maintenance-9.x

---
**Manager**

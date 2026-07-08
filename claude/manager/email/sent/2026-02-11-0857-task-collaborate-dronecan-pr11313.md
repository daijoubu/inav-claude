# Task Assignment: Collaborate on DroneCAN PR #11313

**Date:** 2026-02-11 08:57
**From:** Manager
**To:** Developer
**Project:** collaborate-dronecan-pr11313
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 15-25 hours

## Task

Collaborate with @daijoubu on PR #11313 to help complete the DroneCAN/libcanard implementation for INAV. The PR adds foundational CAN bus support and needs additional features and testing.

## Background

PR #11313 introduces DroneCAN protocol support using libcanard:
- Core CAN framework and libcanard integration
- FDCAN driver for STM32H7, bxCAN driver for STM32F7
- GPS receiver and battery voltage sensor drivers
- 44 unit tests
- Base branch: maintenance-10.x

This is a significant contribution that will enable INAV to support DroneCAN-compatible sensors and devices, expanding hardware compatibility and ecosystem integration.

## What to Do

1. **Research & Setup**: Clone daijoubu's branch, review the implementation, understand libcanard and DroneCAN specification
2. **CAN Current Sensor**: Implement current sensor driver following the existing voltage sensor pattern, add unit tests
3. **Parameter Get/Set**: Implement DroneCAN parameter protocol for reading/writing config parameters, add unit tests
4. **HITL Testing**: Set up and run hardware-in-the-loop tests, document results
5. **Documentation**: Write wiki docs for DroneCAN feature including setup, configuration, and troubleshooting

## Success Criteria

- [ ] CAN current sensor driver implemented and tested
- [ ] Parameter get/set protocol working
- [ ] HITL testing completed with documented results
- [ ] Wiki documentation written
- [ ] Changes submitted to PR author for review

## Important Notes

This is collaboration with an external contributor. Code should follow patterns established in the PR. Commits may be submitted as suggestions or separate PRs to merge into daijoubu's branch.

## References

- **PR:** https://github.com/iNavFlight/inav/pull/11313
- **Issue:** https://github.com/iNavFlight/inav/issues/11128
- **libcanard:** https://github.com/dronecan/libcanard
- **DroneCAN Spec:** https://dronecan.github.io/

## Project Directory

`claude/projects/active/collaborate-dronecan-pr11313/`

**Branch:** From maintenance-10.x (coordinate with daijoubu's branch)

---
**Manager**

# Task Assignment: Fix Build Errors on PR #11313

**Date:** 2026-02-13 12:44
**From:** Manager
**To:** Developer
**Project:** pr-11313-build-fixes
**Priority:** HIGH
**Estimated Effort:** 4-6 hours

## Task

Fix all build errors and code quality issues identified in PR #11313 to make it ready for merge. This PR adds DroneCAN protocol support to iNav using libcanard.

## Background

PR #11313 adds DroneCAN protocol support to iNav but has critical issues blocking merge:
- 7 bugs identified by Qodo code review
- 7 code style violations
- Build failures in CI
- DSDL generation needs implementation

## What to Do

1. **Review project documentation** at `claude/projects/active/pr-11313-build-fixes/`:
   - Read `summary.md` for full project overview
   - Review `todo.md` for detailed task breakdown
   - Check Qodo reports for specific issues

2. **Fix identified bugs** (7 total):
   - Buffer overflow in UAVCAN parameters
   - Memory leak in DroneCAN error handling
   - RX packet handling issues
   - TX queue management problems
   - DSDL generation integration
   - Include path resolution
   - Initialization error handling

3. **Address code style violations** (7 total):
   - Fix indentation issues
   - Add proper error handling for snprintf
   - Correct function parameter alignment
   - Update header guards
   - Fix spacing around operators
   - Align multi-line statements
   - Add missing documentation

4. **Implement DSDL build-time generation**:
   - Set up DSDL submodule approach
   - Create build scripts for code generation
   - Integrate with existing build system

5. **Test thoroughly**:
   - Verify SITL builds pass
   - Test hardware target builds
   - Confirm existing DroneCAN functionality works
   - Run Qodo analysis again to verify fixes

## Success Criteria

- [ ] All 7 Qodo-identified bugs fixed
- [ ] All 7 code style rule violations resolved
- [ ] DSDL build-time generation implemented and working
- [ ] CI builds passing (SITL and hardware targets)
- [ ] Existing DroneCAN functionality verified
- [ ] PR ready for re-review and merge

## Project Directory

`claude/projects/active/pr-11313-build-fixes/`

## Branch

Work from `maintenance-9.x` branch (PR #11313 target branch)

## Important Notes

- The `dsdlc-submodule-generation` project is related to DSDL generation work. Consider coordinating efforts or combining approaches.
- Document all fixes clearly in commit messages
- Test both SITL simulation and real hardware if possible
- Ensure backward compatibility with existing DroneCAN implementations

---
**Manager**

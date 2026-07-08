# Task Assignment: Fix Build Errors on PR #11313

**Date:** 2026-02-13
**From:** Manager
**To:** Developer
**Project:** pr-11313-build-fixes
**Priority:** HIGH
**Estimated Effort:** 4-6 hours

## Task

Fix 7 Qodo bugs and 7 rule violations identified on PR #11313 (DroneCAN support with GPS driver). The PR cannot be merged until all Qodo issues are addressed.

## Background

PR #11313 adds DroneCAN protocol support to iNav using libcanard. A Qodo code review identified critical issues blocking the merge:

### Critical Bugs (7)
1. **Generated code committed** - dsdlc_generated files in repo instead of build-time generation
2. **Buffer overflow risk** - Missing DataLength validation
3. **Error handling missing** - Ignored error returns from CAN init/timing functions
4. **Missing header includes** - dronecan.h requires parameter_group.h
5. **MSP enumeration** - PG_ID range not updated
6. **TX queue failure** - Pops on failure, dropping frames
7. **RX loop bug** - Double-decrements counter, skipping messages

### Code Quality Issues (7)
- Various code style and best practice violations

## What to Do

See `claude/projects/active/pr-11313-build-fixes/` for full project details:

1. Review Qodo findings in detail
2. Fix each bug systematically:
   - Bug 1: DSDL build-time generation (submodule)
   - Bug 2: Buffer overflow - add DataLength checks
   - Bug 3: Error handling - check return values
   - Bug 4: Header includes - add parameter_group.h
   - Bug 5: MSP - update PG_ID range
   - Bug 6: TX queue - fix failure handling
   - Bug 7: RX loop - fix counter decrement
3. Fix code style rule violations
4. Rebuild and test
5. Push fixes to PR branch

## Success Criteria

- [ ] All 7 Qodo bugs fixed
- [ ] All 7 rule violations addressed
- [ ] CI builds pass without errors
- [ ] Existing DroneCAN functionality verified
- [ ] DSDL files generated at build time (not committed)
- [ ] PR ready for final review

## Project Directory

`claude/projects/active/pr-11313-build-fixes/`

---
**Manager**
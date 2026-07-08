# Task Assignment: Fix SITL CI Build Errors on PR #11313

**Date:** 2026-02-13 16:11
**From:** Manager
**To:** Developer
**Project:** fix-sitl-ci-build-errors
**Priority:** HIGH
**Estimated Effort:** 2-4 hours

## Task

Fix 2 CI build failures in PR #11313 (DroneCAN SITL implementation):
1. SITL-Windows build error
2. SITL-Mac build error

These are the last blockers preventing the DroneCAN SITL implementation from being merged.

## Background

PR #11313 implements DroneCAN SITL support with SocketCAN driver. The Linux SITL builds pass, but Windows and macOS CI runners are reporting build errors. We need to investigate and fix these platform-specific issues.

## What to Do

1. **Investigate Build Errors**
   - Visit PR #11313 on GitHub
   - Review CI build logs for exact error messages
   - Note the specific compiler errors for Windows and macOS

2. **Root Cause Analysis**
   - Determine if errors are in DroneCAN code or other changes
   - Identify platform-specific issues (toolchain, includes, APIs, path handling)
   - Check for compiler warnings treated as errors

3. **Fix and Test**
   - Apply fixes to resolve the errors
   - Build/test locally if possible to verify fixes
   - Push to PR and verify CI passes all platforms

4. **Validation**
   - Verify Linux, Windows, and macOS all build successfully
   - Verify DroneCAN SITL functionality is not broken
   - Confirm no other CI checks are affected

## Success Criteria

- [ ] Windows SITL build error identified and fixed
- [ ] macOS SITL build error identified and fixed
- [ ] All CI checks pass (Linux, Windows, macOS)
- [ ] Code compiles cleanly
- [ ] No functional regressions
- [ ] PR is ready to merge

## Project Directory

`claude/projects/active/fix-sitl-ci-build-errors/`

## PR Link

[#11313 - DroneCAN SITL Implementation](https://github.com/iNavFlight/inav/pull/11313)

## Recommended Workflow

1. Use `/start-task` to begin work on this task
2. Review CI build logs for exact errors
3. Investigate and apply fixes
4. Push fixes to the PR
5. Wait for CI to complete
6. Send completion report to manager

This is HIGH priority as it's blocking the DroneCAN implementation from being merged.

---
**Manager**

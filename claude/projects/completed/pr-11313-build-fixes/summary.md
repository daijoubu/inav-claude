# Project: Fix macOS SITL CI Build Failure on PR #11313

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix | CI Build Issue
**Created:** 2026-02-13
**Estimated Effort:** 1-2 hours

## Overview

Fix the macOS SITL CI build failure on PR #11313 (DroneCAN support). Currently macOS builds fail while Linux builds pass. This is blocking PR merge.

## Problem

PR #11313 adds DroneCAN protocol support to iNav using libcanard. While Linux SITL builds pass in CI, macOS SITL builds are failing due to:
1. Missing include paths for installed headers
2. Build system configuration differences between Linux and macOS

## Objectives

1. Investigate macOS SITL build failure
2. Identify root cause (header include issues)
3. Apply minimal fix to get macOS SITL builds passing
4. Ensure macOS builds match Linux build behavior
5. Enable PR #11313 to merge

## Scope

**In Scope:**
- Fix macOS SITL CI build failure only
- Adjust include paths or build configuration
- Test locally on macOS or analyze CI logs
- Apply minimal, targeted changes

**Out of Scope:**
- Qodo code review issues (handled separately in dsdlc-submodule-generation project)
- Windows builds
- Hardware target builds
- Functional changes to DroneCAN implementation
- DSDL build-time generation

## Implementation Steps

1. Review CI logs for macOS SITL failure
2. Compare Linux vs macOS build configurations
3. Investigate header include paths
4. Apply minimal fix for macOS includes
5. Trigger CI to verify fix

## Success Criteria

- [ ] macOS SITL builds pass in CI
- [ ] Linux SITL builds still pass
- [ ] PR #11313 CI checks all green
- [ ] PR ready for review and merge

## Estimated Time
1-2 hours

## Priority Justification
HIGH - The macOS SITL build failure blocks PR #11313 from merging, which contains important DroneCAN protocol improvements.

## Related
- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Issue:** [#11128](https://github.com/iNavFlight/inav/issues/11128) (fixed by PR)
- **Project:** dsdlc-submodule-generation (separate DSDL generation work)
- **CI Build Log:** Look for macOS SITL failure logs

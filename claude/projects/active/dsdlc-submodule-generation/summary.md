# Project: Move dsdlc to Git Submodule with Build-time Generation

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Refactoring / Build System
**Created:** 2026-02-11
**Estimated Effort:** 2-4 hours

## Overview

Remove the committed `dsdlc_generated` files from the repository and instead:
1. Add the DSDL definitions as a git submodule
2. Generate the C sources during the build process

This addresses Qodo code review issue #1 on PR #11313.

## Problem

The current implementation commits ~27K lines of auto-generated DroneCAN DSDL codec files directly to the repository. This:
- Makes the repo noisy with generated artifacts
- Can cause non-reproducible builds
- Makes updates to DSDL definitions harder to track
- Violates best practices for generated code

## Solution

1. Remove `src/main/drivers/dronecan/dsdlc_generated/` from git tracking
2. Add libcanard DSDL definitions as a git submodule
3. Add CMake rules to generate the codec files during build
4. Update `.gitignore` to exclude generated files

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Qodo Issue:** #1 - dsdlc_generated code committed

## References

- libcanard dsdlc tool: https://github.com/dronecan/libcanard
- DSDL definitions: https://github.com/DroneCAN/DSDL

## Success Criteria

- [ ] Generated files removed from git history
- [ ] DSDL submodule added
- [ ] Build generates codec files automatically
- [ ] CI builds pass
- [ ] No functional changes to DroneCAN behavior

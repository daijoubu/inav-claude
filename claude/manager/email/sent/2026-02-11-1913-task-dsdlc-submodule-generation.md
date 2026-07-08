# Task Assignment: Move dsdlc to Git Submodule with Build-time Generation

**Date:** 2026-02-11 19:13
**From:** Manager
**To:** Developer
**Project:** dsdlc-submodule-generation
**Priority:** MEDIUM
**Estimated Effort:** 4-6 hours

## Task

Remove the committed dsdlc_generated files (~27K lines) from the repository and instead add the DSDL definitions as a git submodule with C sources generated during the build process using the dsdlc tool.

## Background

The current implementation commits auto-generated DroneCAN DSDL codec files directly to the repository. This makes the repo noisy, can cause non-reproducible builds, and violates best practices for generated code. This task addresses Qodo code review issue #1 on PR #11313.

## What to Do

1. **Add DSDL submodule**
   - Add libcanard DSDL definitions as a git submodule
   - Reference: https://github.com/DroneCAN/DSDL
   - Place in appropriate location (suggest `src/main/drivers/dronecan/dsdl/`)

2. **Configure build-time generation**
   - Update `cmake/main.cmake` to add generation rules
   - Generate C codec files during build using dsdlc tool
   - Integrate dsdlc invocation into the CMake build process
   - Reference libcanard tool: https://github.com/dronecan/libcanard

3. **Remove generated files from git tracking**
   - Delete `src/main/drivers/dronecan/dsdlc_generated/` directory from git
   - Update `.gitignore` to exclude generated output directory
   - Ensure git no longer tracks the ~27K lines of generated code

4. **Verify build process**
   - CI builds pass with new configuration
   - Local builds successfully generate codec files
   - No functional changes to DroneCAN behavior

## Files to Check

- `src/main/drivers/dronecan/dsdlc_generated/` - to be removed from git
- `cmake/main.cmake` - add generation rules
- `.gitignore` - exclude generated files
- Existing DroneCAN driver code - verify compatibility

## Success Criteria

- [ ] Generated files removed from git tracking
- [ ] DSDL submodule added and correctly configured
- [ ] Build generates codec files automatically
- [ ] CI builds pass
- [ ] No functional changes to DroneCAN behavior
- [ ] Branch ready for PR from add-libcanard

## Project Directory

`claude/projects/active/dsdlc-submodule-generation/`

## Branch Information

**Base branch:** add-libcanard (PR #11313)
**Create branch for this work:** Create a feature branch from add-libcanard

---
**Manager**

# Project: Reorganize DSDL Generated Files - Cleanup & Documentation

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Code Organization / Documentation
**Created:** 2026-02-11
**Estimated Effort (Developer):** 2-3 hours (inventory + documentation)
**Estimated Effort (Manager):** 1-2 hours (move files + update build)

## Overview

**Developer provides inventory and documentation; Manager reorganizes files** to clean up the DSDL codec file structure and document how to add new messages.

This addresses Qodo code review issue #1 on PR #11313.

## Problem

The current implementation commits ~27K lines of DroneCAN DSDL codec files in `src/main/drivers/dronecan/dsdlc_generated/`. This:
- Makes the repo noisy with generated artifacts
- Includes many files not actually used by INAV
- Lacks documentation on DSDL version and how to regenerate/extend messages
- Violates best practices for generated code

## Solution Approach

1. **Move generated files** from `src/main/drivers/dronecan/dsdlc_generated/` to `lib/main/dronecan_generated/`
2. **Keep only files currently used** by INAV (reduce 27K lines to ~5-7K)
3. **Document DSDL version** that was used to generate files
4. **Document process** for developers to add new DroneCAN messages
5. **Developer role:** Research, inventory files, document the process
6. **Manager role:** Execute reorganization, create documentation

## Key Components to Understand

**DSDL Code Generation:**
- dsdlc tool: Part of libcanard/DroneCAN ecosystem
- Input: DSDL definition files (.yaml)
- Output: C header/source files
- Current state: files already generated and committed

**DroneCAN DSDL Repository:**
- Source: https://github.com/DroneCAN/DSDL
- Contains all standard DroneCAN message definitions
- INAV currently uses a specific version/commit

**Current Generated Files:**
- Location: `src/main/drivers/dronecan/dsdlc_generated/`
- Contains ~27K lines of generated C code
- Many files not actually used by INAV

## What Developer Should Research & Document

1. **File Inventory:**
   - List all files in `src/main/drivers/dronecan/dsdlc_generated/`
   - Identify which files are actually #included in INAV code
   - Identify which files are unused/redundant
   - Map each used file to its DSDL message definition

2. **DSDL Version Documentation:**
   - Determine which version of DroneCAN DSDL was used
   - Check libcanard repository for dsdlc tool version
   - Document the commit/tag of DroneCAN DSDL repo used
   - Document dsdlc tool usage (command-line options, invocation)

3. **Message Extension Process:**
   - How to identify new messages needed from DroneCAN DSDL
   - How to run dsdlc to generate C code from .yaml definitions
   - How to integrate new generated files into INAV
   - What CMake changes are needed to include new files

4. **Build System Impact:**
   - Current CMakeLists.txt references (cmake/dsdlc_generated.cmake)
   - Include path configuration (where generated headers are expected)
   - How files would move from src/main/drivers/dronecan/dsdlc_generated/ to lib/main/dronecan_generated/

## Developer Deliverable

A comprehensive **DSDL-GUIDE.md** document in the project directory containing:

```markdown
# DroneCAN DSDL Codec Management Guide

## Current DSDL Version
- DroneCAN DSDL Repository: https://github.com/DroneCAN/DSDL
- Commit/Tag Used: [version info]
- dsdlc Tool Version: [version info]

## Currently Used Messages
- List of all .c/.h files in the current set
- Which INAV features use each message type

## Adding New DroneCAN Messages

### Step 1: Identify Message
[Instructions for finding message in DroneCAN/DSDL]

### Step 2: Generate C Code
[Instructions for running dsdlc tool]

### Step 3: Integrate into INAV
[Instructions for adding to CMakeLists.txt and code]

### Step 4: Verify
[Testing and validation steps]

## File Organization
- Generated files location: lib/main/dronecan_generated/
- Include paths configuration
- CMake reference file: cmake/dsdlc_generated.cmake

## Reference
[Links to dsdlc documentation, DroneCAN DSDL spec]
```

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **Qodo Issue:** #1 - dsdlc_generated code committed
- **DroneCAN DSDL Repo:** https://github.com/DroneCAN/DSDL
- **libcanard:** https://github.com/dronecan/libcanard

## References for Developer Research

### Git Submodules
- Official guide: https://git-scm.com/book/en/v2/Git-Tools-Submodules
- Git filter-branch: https://git-scm.com/docs/git-filter-branch
- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/ (safer alternative)

### CMake Code Generation
- Custom commands: https://cmake.org/cmake/help/latest/command/add_custom_command.html
- Custom targets: https://cmake.org/cmake/help/latest/command/add_custom_target.html
- File(GLOB): https://cmake.org/cmake/help/latest/command/file.html

### INAV Build System
- INAV CMakeLists.txt: `inav/CMakeLists.txt` (main entry point)
- SITL build config: `inav/cmake/sitl.cmake`
- Target configuration: `inav/cmake/`
- Search for existing `add_custom_command()` usage in INAV to see patterns

### DroneCAN/libcanard
- libcanard README: https://github.com/dronecan/libcanard
- DSDL specification: https://github.com/DroneCAN/DSDL
- dsdlc tool docs (if available): Check libcanard tools/ directory

## Success Criteria

- [ ] Developer provides complete DSDL-GUIDE.md
- [ ] Guide documents current DSDL version and dsdlc tool version used
- [ ] Guide identifies which generated files are actually used by INAV
- [ ] Guide documents process to add new DroneCAN messages
- [ ] Guide includes dsdlc command syntax and examples
- [ ] Manager can follow guide to reorganize files to lib/main/
- [ ] Manager can remove unused generated files
- [ ] Build still compiles and works after file reorganization
- [ ] No functional changes to DroneCAN behavior
- [ ] Generated file count reduced from ~27K lines to ~5-7K lines

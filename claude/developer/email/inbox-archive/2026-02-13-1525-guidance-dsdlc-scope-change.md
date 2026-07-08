# Guidance: Scope Change - dsdlc-submodule-generation Project

**Date:** 2026-02-13 15:25
**From:** Manager
**To:** Developer
**Project:** dsdlc-submodule-generation
**Priority:** MEDIUM
**Type:** Scope Change / Guidance

## Notification: Project Scope Changed

The dsdlc-submodule-generation project scope has been revised. **You are now providing guidance/research rather than implementing the changes.**

## Your New Role

Instead of implementing the migration yourself, you will:

1. **Research** the tools and build system involved
2. **Document** step-by-step instructions for me (the manager) to implement
3. **Provide** a comprehensive implementation guide

## What You Need to Research & Document

### 1. DSDL Code Generation Tool
- Locate dsdlc tool in libcanard repository
- Document tool location, prerequisites, and dependencies
- Test tool invocation locally if possible
- Understand input/output file structure

### 2. CMake Build System Integration
- Review INAV's existing CMakeLists.txt patterns
- Find existing `add_custom_command()` and `add_custom_target()` examples in INAV
- Study cmake/sitl.cmake and cmake/ directory structure
- Document how generated files should be configured

### 3. Git Submodule Setup
- Decide optimal submodule location
- Research submodule workflow (add, clone, update)
- Document git history cleanup approach (filter-branch vs BFG)

### 4. Implementation Guide (MAIN DELIVERABLE)
Create `IMPLEMENTATION-GUIDE.md` in the project directory with:
- Tool location and prerequisites
- Phase 1: Add Git Submodule (exact git commands)
- Phase 2: Configure CMake Generation (exact CMake code, copy-paste ready)
- Phase 3: Update .gitignore
- Phase 4: Remove Generated Files from Git
- Phase 5: Test Build
- Troubleshooting section
- Reference links

## Key Resources for Research

**Git Submodules:**
- https://git-scm.com/book/en/v2/Git-Tools-Submodules
- https://git-scm.com/docs/git-filter-branch
- https://rtyley.github.io/bfg-repo-cleaner/ (safer history rewriting)

**CMake Code Generation:**
- https://cmake.org/cmake/help/latest/command/add_custom_command.html
- https://cmake.org/cmake/help/latest/command/add_custom_target.html
- https://cmake.org/cmake/help/latest/command/file.html

**INAV Build System:**
- `inav/CMakeLists.txt` - Main entry point
- `inav/cmake/sitl.cmake` - SITL build config
- Search existing INAV code for `add_custom_command()` patterns

**DroneCAN/libcanard:**
- https://github.com/dronecan/libcanard
- https://github.com/DroneCAN/DSDL

## Updated Todo List

Your new todo.md has been updated with research phases:

### Phase 1: Tool & Environment Research
- Locate dsdlc tool in libcanard
- Document prerequisites and dependencies
- Test tool invocation
- Review DroneCAN DSDL repository

### Phase 2: CMake Build System Analysis
- Review INAV CMakeLists.txt
- Find existing code generation examples
- Study include path configuration
- Document patterns for generated files

### Phase 3: Git Submodule Research
- Test submodule workflow locally
- Research history cleanup options
- Document submodule initialization

### Phase 4: Create Implementation Guide
- Write IMPLEMENTATION-GUIDE.md
- Include exact commands and CMake code
- Add troubleshooting section
- Create validation checklist

### Phase 5: Review & Documentation
- Test guide walkthrough
- Verify all commands
- Ensure clarity and completeness

## Why This Approach

This gives you the opportunity to:
- Deep-dive into INAV's build system
- Learn CMake code generation patterns
- Understand git workflows
- Provide me with a repeatable, well-documented process

And it gives me the opportunity to:
- Actually implement and learn by doing
- Understand the system better through hands-on work
- Have a reference guide for future similar tasks

## Deliverable

**Primary:** `IMPLEMENTATION-GUIDE.md` that I can follow step-by-step to:
1. Add the DSDL definitions as a git submodule
2. Configure CMake to generate codec files at build time
3. Remove generated files from git history
4. Validate the build works automatically

**When complete:** Send completion report to me with the guide attached.

## Questions?

If anything is unclear about the new scope, please ask!

---
**Manager**

# Guidance: Revised Scope - DSDL Cleanup Approach

**Date:** 2026-02-13 09:00
**From:** Manager
**To:** Developer
**Project:** dsdlc-submodule-generation
**Status:** SCOPE REVISED

## New Direction: Pragmatic Approach

After further consideration, we're taking a simpler, more pragmatic approach than either submodules or build-time generation.

**New Plan:**
1. Move the DroneCAN DSDL generated files from `src/main/drivers/dronecan/dsdlc_generated/` to `lib/main/dronecan_generated/`
2. Remove unused generated files (reduce from ~27K lines to ~5-7K lines)
3. Document the DSDL version that was used to generate the current files
4. Document the process for developers to add new DroneCAN messages

This approach:
- ✅ Reduces repo bloat (keep only what we use)
- ✅ Separates generated code from source code (better organization)
- ✅ Maintains reproducibility (document the version used)
- ✅ Enables future extension (clear process for new messages)
- ✅ No build system complexity (files stay committed)
- ✅ Respects INAV's constraints (no submodules, no external tool requirements)

## Your New Research Tasks

### Phase 1: File Inventory
- List all files currently in `src/main/drivers/dronecan/dsdlc_generated/`
- Search INAV codebase for #includes of these files
- Identify which files are actually used
- Create mapping: used file → DSDL message type
- Count current lines vs. just used files

### Phase 2: DSDL Version Research
- Determine which version/commit of DroneCAN/DSDL was used
- Locate dsdlc tool in libcanard repo
- Document dsdlc command-line options and invocation syntax
- Test tool locally if possible

### Phase 3: Message Extension Documentation
- Research how to identify new messages in DroneCAN/DSDL
- Document steps to generate C code for new messages
- Document how to integrate generated files into INAV
- Review cmake/dsdlc_generated.cmake structure

### Phase 4: Create DSDL-GUIDE.md

Create `DSDL-GUIDE.md` in the project directory with:

**Section 1: Current DSDL Version**
- DroneCAN DSDL repository URL and version/commit
- dsdlc tool version and location
- When it was last updated

**Section 2: Currently Used Messages**
- List of all .c/.h files that are actively used
- Which INAV features use each message type (e.g., "Battery info used by power management")
- Total lines of code currently kept

**Section 3: Adding New DroneCAN Messages**

Step-by-step instructions for developers:
1. How to identify needed message in DroneCAN/DSDL repo
2. How to run dsdlc to generate C code
3. How to integrate generated files into INAV
4. Which CMake files to update
5. Testing and validation steps

Include concrete examples and commands (copy-paste ready).

**Section 4: File Organization**
- Current location: src/main/drivers/dronecan/dsdlc_generated/ (to be moved)
- New location: lib/main/dronecan_generated/
- Include path configuration
- CMake reference file: cmake/dsdlc_generated.cmake

**Section 5: Reference & Tools**
- Links to DroneCAN/DSDL repo
- Links to libcanard dsdlc documentation
- dsdlc command reference

## Deliverables

When complete, send completion report with:

1. **DSDL-GUIDE.md** - Comprehensive guide (primary deliverable)
2. **File Inventory**
   - Complete list of files currently in dsdlc_generated/
   - List of used files (to keep and move to lib/main/)
   - List of unused files (to be deleted)
   - Line count comparison
3. **DSDL Version Info**
   - Repository and commit used
   - dsdlc tool version
   - Generation date/notes

## Manager's Implementation

After you complete the research and guide, I will:

1. Create `lib/main/dronecan_generated/` directory
2. Move used files from src/main/ to lib/main/
3. Delete the unused files
4. Update CMake references
5. Update include paths
6. Test build for SITL and hardware targets
7. Verify DroneCAN functionality still works
8. Create PR with the changes

## Questions?

This approach is much simpler than the previous scope, focuses on practical cleanup and documentation, and should address the Qodo code review issue while keeping things maintainable.

---
**Manager**

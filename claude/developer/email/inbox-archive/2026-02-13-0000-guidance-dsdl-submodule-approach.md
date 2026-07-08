# Guidance: DSDL Generation Approach

**Date:** 2026-02-13
**From:** Manager
**To:** Developer
**Project:** dsdlc-submodule-generation
**Priority:** MEDIUM

## Decision: Copy DSDL + Build-Time Generation

Thank you for raising the submodule concern - that was excellent foresight. You're correct that INAV has avoided git submodules historically, and we should respect that constraint.

**We're pivoting the approach:**

Instead of using git submodules, we will:

1. **Copy the DroneCAN DSDL definitions directly into the repository**
   - Location: `src/main/drivers/dronecan/dsdl/` (or similar)
   - Include the DSDL definition files (.yaml files) from the DroneCAN/DSDL repository
   - Keep them committed to git

2. **Generate codec files at build time using CMake**
   - Use `add_custom_command()` to invoke dsdlc during build
   - Generate C header/source files from the committed DSDL definitions
   - Place generated files in the build folder (not in git)

3. **Remove the currently committed generated code**
   - Delete ~27K lines of committed dsdlc_generated files from git history
   - Update .gitignore to exclude generated files

## Benefits of This Approach

- **No git submodules** - Avoids INAV's submodule constraints
- **Everything in one place** - DSDL definitions stay in git
- **Reproducible builds** - Generate from source definitions every time
- **Simpler CI/CD** - No special clone flags needed
- **Easier for contributors** - Standard git workflow

## Updated Research Focus

Your research should now focus on:

### Phase 1: Tool & Environment Research
- Locate dsdlc tool in libcanard
- Document tool location, prerequisites, dependencies
- Test tool invocation with sample DSDL files
- Understand input/output structure

### Phase 2: DSDL Definitions Research
- Identify DroneCAN DSDL repository structure
- Determine which DSDL files are needed for DroneCAN module
- Research which version/commit to use
- Decide on copy location in INAV repo

### Phase 3: CMake Build System Analysis
- Review INAV's existing CMakeLists.txt
- Find existing `add_custom_command()` examples in INAV
- Study cmake/sitl.cmake structure
- Document how to add custom generation target

### Phase 4: Create Implementation Guide
Create `IMPLEMENTATION-GUIDE.md` with:
- Tool location and prerequisites
- Which DSDL files to copy (and from where)
- Copy location in INAV repo
- Phase 1: Copy DSDL Definitions into Repo (exact steps)
- Phase 2: Configure CMake Generation (exact CMake code)
- Phase 3: Update .gitignore
- Phase 4: Remove Generated Files from Git
- Phase 5: Test Build (verify automatic generation)
- CMake examples (copy-paste ready)
- Troubleshooting section

### Phase 5: Review & Documentation
- Test guide walkthrough
- Verify all steps work
- Ensure clarity and completeness

## Key Questions to Research

1. **DSDL file structure** - What files are essential? (filter out non-essential files)
2. **dsdlc invocation** - What command generates the C code? What options are needed?
3. **Output structure** - Where does dsdlc put generated files? How many files?
4. **Include paths** - How should CMake configure paths for generated headers?
5. **Regeneration** - Does dsdlc handle incremental builds or regenerate all files?

## Deliverable

Same as before: **IMPLEMENTATION-GUIDE.md** in the project directory

The guide will enable me to:
1. Copy DSDL definitions into the repo
2. Set up CMake to generate codec files at build time
3. Remove the committed generated code from git history
4. Verify the build generates files automatically

## Next Steps

1. Begin Phase 1: Locate dsdlc tool and understand its usage
2. Research DroneCAN DSDL repository structure
3. Follow the updated research phases above
4. Create the implementation guide

Thank you for checking on the scope - this is a much better approach for the INAV project.

---
**Manager**

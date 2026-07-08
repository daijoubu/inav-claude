# Task Assignment: DSDL Generated Files Inventory & Documentation

**Date:** 2026-02-14 10:00
**From:** Manager
**To:** Developer
**Project:** dsdlc-submodule-generation
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours

## Task

This project addresses Qodo code review issue #1 on PR #11313. The current implementation commits ~27K lines of DroneCAN DSDL codec files in `src/main/drivers/dronecan/dsdlc_generated/`. This includes many unused files and lacks documentation on how to add new messages.

## Background

The INAV codebase currently includes a large number of generated DSDL files but:
- Many files are unused in the codebase
- No documentation exists on how to add new messages
- Version/commit of DSDL repository is unclear
- Integration process is not documented

## What to Do

### Phase 1: File Inventory
1. List all files in `src/main/drivers/dronecan/dsdlc_generated/`
2. Search INAV codebase for #includes of dsdlc_generated files
3. Identify which files are actually used vs unused
4. Create mapping: used file → DSDL message type

### Phase 2: DSDL Version Research
1. Determine DroneCAN DSDL repository version/commit used
2. Check libcanard for dsdlc tool version info
3. Document tool prerequisites and command-line options

### Phase 3: Message Extension Documentation
1. Document how to run dsdlc for new messages
2. Document how generated files integrate into INAV
3. Review cmake/dsdlc_generated.cmake structure

### Phase 4: Create DSDL-GUIDE.md
1. Document current DSDL repository and version/commit
2. List all currently used messages/files
3. Write "Adding New DroneCAN Messages" section with steps
4. Include dsdlc command examples

## Success Criteria

- [ ] Complete inventory of used vs unused files documented
- [ ] DSDL-GUIDE.md created with all sections
- [ ] Guide includes dsdlc command examples (copy-paste ready)
- [ ] List of unused files to remove provided
- [ ] List of files to keep/move to lib/main/ provided

## Project Directory

`claude/projects/active/dsdlc-submodule-generation/`

## Base Branch

`maintenance-9.x` (INAV firmware)

## Notes

- Coordinate with Security Analyst if any security concerns arise during file review
- Reference PR #11313 for context on the original code review

---
**Manager**

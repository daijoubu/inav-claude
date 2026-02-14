# Todo: DSDL Generated Files Cleanup & Documentation

## Phase 1: File Inventory (Developer)

- [ ] List all files in `src/main/drivers/dronecan/dsdlc_generated/`
- [ ] Search INAV codebase for #includes of dsdlc_generated files
- [ ] Identify which files are actually used
- [ ] Identify which files are not used/redundant
- [ ] Create mapping: used file → DSDL message type
- [ ] Count lines: total vs. actually used

## Phase 2: DSDL Version Research (Developer)

- [ ] Determine DroneCAN DSDL repository version/commit used
- [ ] Check libcanard for dsdlc tool version info
- [ ] Locate dsdlc tool in libcanard repository
- [ ] Document tool prerequisites and command-line options
- [ ] Document tool invocation syntax for generating C code
- [ ] Test dsdlc tool locally if possible

## Phase 3: Message Extension Documentation (Developer)

- [ ] Research how to identify needed messages in DroneCAN/DSDL
- [ ] Document steps to run dsdlc for new messages
- [ ] Document how generated files are integrated into INAV
- [ ] Review cmake/dsdlc_generated.cmake structure
- [ ] Understand include path configuration
- [ ] Create step-by-step guide for adding new messages

## Phase 4: Create DSDL-GUIDE.md (Developer)

Create `DSDL-GUIDE.md` in project directory:

- [ ] Document current DSDL repository and version/commit
- [ ] Document dsdlc tool version and location
- [ ] List all currently used messages/files
- [ ] Show which INAV features use each message type
- [ ] Write "Adding New DroneCAN Messages" section with steps
- [ ] Include dsdlc command examples (copy-paste ready)
- [ ] Document file organization structure
- [ ] Include troubleshooting/FAQ section
- [ ] Add reference links to DroneCAN/DSDL and libcanard

## Phase 5: Developer Review & Completion (Developer)

- [ ] Verify all information is accurate
- [ ] Test that steps documented actually work
- [ ] Add illustrations/examples if helpful
- [ ] Create summary checklist for manager
- [ ] Review for clarity and completeness

## Completion (Developer)

- [ ] DSDL-GUIDE.md created and complete
- [ ] File inventory completed and documented
- [ ] Send completion report to manager with:
  - [ ] DSDL-GUIDE.md attached
  - [ ] List of unused files to remove
  - [ ] List of files to keep/move to lib/main/
- [ ] Archive workspace files

## Manager Implementation (Will follow after developer completes)

- [ ] Create lib/main/dronecan_generated/ directory
- [ ] Move used files from src/main/drivers/dronecan/dsdlc_generated/ to lib/main/dronecan_generated/
- [ ] Delete unused generated files
- [ ] Update CMake references (cmake/dsdlc_generated.cmake)
- [ ] Update include paths in CMakeLists.txt
- [ ] Verify build still compiles for SITL and hardware targets
- [ ] Verify DroneCAN functionality still works
- [ ] Create PR or commit with changes
- [ ] Report completion to project

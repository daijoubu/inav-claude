# Todo: dsdlc Submodule Generation

## Phase 1: Research

- [ ] Identify DSDL source repository (DroneCAN/DSDL)
- [ ] Understand dsdlc tool requirements
- [ ] Review how other projects handle DSDL generation
- [ ] Determine if dronecan_dsdlc is available as a tool

## Phase 2: Implementation

- [ ] Add DSDL definitions as git submodule
- [ ] Create CMake target for dsdlc generation
- [ ] Configure output directory in build folder
- [ ] Update include paths for generated headers
- [ ] Test local build with generation

## Phase 3: Cleanup

- [ ] Remove dsdlc_generated from git tracking
- [ ] Add generated path to .gitignore
- [ ] Update documentation if needed

## Phase 4: Validation

- [ ] Build SITL successfully
- [ ] Build hardware target successfully
- [ ] Run existing DroneCAN tests
- [ ] CI passes

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created or existing PR updated
- [ ] Completion report sent

# Todo: Add INAV Target for SDMODELH7V2

## Phase 1: Create Target Files

- [ ] Create `inav/src/main/target/SDMODELH7V2/` directory
- [ ] Create `target.h` — pin definitions, peripheral config, timer/DMA mappings
- [ ] Create `target.c` — timer hardware definitions, channel mappings
- [ ] Create `CMakeLists.txt` — target build definition

## Phase 2: Verify

- [ ] Target compiles cleanly
- [ ] Timer/DMA conflict check passes
- [ ] Pin mappings cross-referenced against BF and AP definitions
- [ ] Flash size within budget

## Completion

- [ ] Code compiles
- [ ] PR created on maintenance-9.x
- [ ] Completion report sent to manager

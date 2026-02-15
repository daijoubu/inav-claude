# Todo: Hide Motor Direction Radio Box for Fixed Wing

## Phase 1: Investigation

- [ ] Find the motor direction radio box in configurator UI code
- [ ] Identify how aircraft type is determined in that context
- [ ] Check if similar conditional visibility patterns exist elsewhere

## Phase 2: Implementation

- [ ] Add condition to hide motor direction radio box for fixed wing
- [ ] Ensure it remains visible for multirotors and other types

## Phase 3: Validation

- [ ] Test with fixed wing aircraft type — radio box hidden
- [ ] Test with multirotor aircraft type — radio box visible
- [ ] No regressions in other tabs or aircraft types

## Completion

- [ ] Code compiles / configurator runs
- [ ] PR created against maintenance-9.x (inav-configurator)
- [ ] Completion report sent to manager

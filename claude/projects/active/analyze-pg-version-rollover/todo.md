# Todo: Analyze PG Version Rollover Impact

## Phase 1: Identify At-Risk Parameter Groups

- [x] Find all PG_REGISTER_* calls in codebase
- [x] Extract version numbers from each registration
- [x] Create list of PGs sorted by version number
- [x] Identify PGs at version 12+ (approaching rollover)
- [x] Check `cmake/*pg*` in `pg-version-check-action` branch for additional version info
- [x] Document current state

## Phase 2: Understand Version Comparison Logic

- [x] Read `src/main/config/parameter_group.h`
  - [x] Understand version storage (4-bit field)
  - [x] Study version extraction macro/function
- [x] Read `src/main/config/parameter_group.c`
  - [x] Find pgLoad() function
  - [x] Trace version comparison logic
  - [x] Identify where version mismatch is detected
  - [x] Understand what happens on mismatch
- [x] Check for any other code that compares PG versions

## Phase 3: Analyze Rollover Scenario

- [x] Determine version comparison method
  - [x] Is it equality check only?
  - [x] Is it greater/less than comparison?
  - [x] Is comparison signed or unsigned?
- [x] Test rollover scenario logic
  - [x] What happens: stored=15, current=0?
  - [x] What happens: stored=0, current=15?
  - [x] What happens: stored=14, current=0?
- [x] Document the behavior

## Phase 4: Assess Impact

- [x] Determine user impact
  - [x] Do settings load correctly?
  - [x] Do settings reset to defaults?
  - [x] Do settings corrupt?
  - [x] Is there any error message?
- [x] Check for edge cases
  - [x] Multiple version rollovers (0→15→0 again)
  - [x] Downgrade scenarios
- [x] Evaluate severity
  - [x] Is this safe?
  - [x] Is this inconvenient?
  - [x] Is this dangerous?

## Phase 5: Develop Recommendations

- [x] If rollover works correctly:
  - [x] Document the behavior
  - [x] Add to PG documentation
  - [x] No code changes needed

- [x] If rollover causes issues:
  - [x] Identify specific problem
  - [x] Research mitigation options
  - [x] Evaluate each option's feasibility
  - [x] Recommend best approach
  - [x] Estimate implementation effort

## Completion

- [x] Analysis complete and documented
- [x] Rollover behavior clearly explained
- [x] User impact assessed
- [x] Recommendations provided
- [x] Findings added to PG documentation
- [ ] Send completion report to manager

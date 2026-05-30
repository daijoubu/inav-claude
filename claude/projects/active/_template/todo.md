# Todo: <PROJECT NAME>

## Phase 1: Reproduce (bug fix) OR Document + Failing Test (feature)

**For bug fixes:** Reproduce the bug before touching any code. Confirm root cause.
- [ ] Reproduce the bug with a concrete test case or steps
- [ ] Confirm root cause — don't fix until the cause is understood

**For features:** Write documentation and a failing test before any implementation.
Documentation defines what behavior the user expects; the test makes that concrete.
When the test passes and behavior matches the docs, the feature may be complete.
This prevents implementing behavior that surprises users or goes down wrong rabbit holes.
- [ ] Write user-facing documentation describing the expected behavior
- [ ] Write a failing test that exercises that behavior end-to-end
- [ ] Confirm the test fails for the right reason (feature not yet implemented, not a setup error)

## Phase 2: Implementation

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Phase 3: Verify

**For bug fixes:**
- [ ] Confirm the original reproduction case no longer exhibits the bug
- [ ] Confirm related/adjacent behavior is unchanged

**For features:**
- [ ] Failing test from Phase 1 now passes
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Edge cases and error paths behave sensibly

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created
- [ ] Completion report sent to manager

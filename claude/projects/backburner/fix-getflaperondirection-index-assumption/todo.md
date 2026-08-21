# Todo List: Fix getFlaperonDirection() Index Assumption

## Phase 1: Decide approach

- [ ] Confirm whether `inputSource`/rule metadata is available at the point
      `getFlaperonDirection()` is called, cheaply enough to check the real
      mixer function instead of the channel number
- [ ] If not, decide on documentation/validation fallback instead

## Phase 2: Implement

- [ ] Fix `getFlaperonDirection()` (`src/main/flight/servos.c:133-140`) per
      chosen approach
- [ ] Update/add unit test coverage for the new behavior

## Completion

- [ ] Existing servo mixer tests passing
- [ ] Completion report sent to manager

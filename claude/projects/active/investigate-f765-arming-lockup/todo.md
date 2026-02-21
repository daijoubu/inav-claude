# Todo: Investigate F765/H743 Arming Lockup

## Phase 1: Code Analysis

- [ ] Find and review F765 blackbox changes in 8.0.0
  - [ ] `git log --oneline v7.1.2..v8.0.0 -- src/main/blackbox/`
  - [ ] `git log --oneline v7.1.2..v8.0.0 -- src/main/drivers/sdcard/`
  - [ ] Review each commit for potential race conditions
- [ ] Analyze arming sequence in `fc_core.c`
  - [ ] What initializes when ARMING_FLAG is set?
  - [ ] What blackbox operations start at arm?
  - [ ] What GPS/nav operations change at arm?
- [ ] Map DMA channels on F765
  - [ ] Which DMA streams used for SD card?
  - [ ] Which DMA streams used for PWM/servo?
  - [ ] Which DMA streams used for UART (GPS)?
  - [ ] Any shared DMA controllers?
- [ ] Review interrupt priorities
  - [ ] Check NVIC priorities for SD, PWM, GPS
  - [ ] Look for priority inversion risks

## Phase 2: Identify Critical Code Paths

- [ ] Trace arming code path
  - [ ] `tryArm()` function
  - [ ] `ENABLE_ARMING_FLAG(ARMED)` effects
  - [ ] Motor/servo output activation
- [ ] Trace blackbox arm behavior
  - [ ] When does logging actually start?
  - [ ] SD card write initiation
  - [ ] Buffer allocation/initialization
- [ ] Trace GPS fix handling
  - [ ] What happens when `STATE(GPS_FIX)` becomes true?
  - [ ] AHRS reconfiguration at fix
  - [ ] Navigation state changes
- [ ] Identify shared resources
  - [ ] Global locks or mutexes
  - [ ] Shared buffers
  - [ ] DMA completion flags

## Phase 3: Specific Checks

- [ ] Check for blocking operations at arm time
  - [ ] SD card sync operations?
  - [ ] Flash writes?
  - [ ] Config saves?
- [ ] Check for interrupt disable periods
  - [ ] Critical sections in arming?
  - [ ] DMA interrupt handling?
- [ ] Check timing assumptions
  - [ ] Hard-coded delays?
  - [ ] Timeout handling?
  - [ ] Busy-wait loops?

## Phase 4: Related Issues Review

- [ ] Read #10646 for additional clues
- [ ] Read #10659 for additional clues
- [ ] Read #10800 for additional clues
- [ ] Read #11007 (F765 in-flight lockup) for additional clues
- [ ] Look for common patterns across all issues

## Phase 5: Testing Strategy

- [ ] Define test matrix
  - [ ] With/without SD card
  - [ ] Different logging rates (off, 3%, 10%, 32%)
  - [ ] Different PWM protocols (Standard, Oneshot, Dshot)
  - [ ] Arm before/after GPS fix
- [ ] SITL testing plan (if applicable)
- [ ] Hardware testing plan (if F765 available)

## Phase 6: Documentation

- [ ] Document findings in summary.md
- [ ] Create timeline of relevant commits
- [ ] Diagram DMA/interrupt interactions
- [ ] Propose fix or workaround

## Completion

- [ ] Root cause identified or narrowed down
- [ ] Findings documented
- [ ] Send completion report to manager
- [ ] Consider posting findings to GitHub issue

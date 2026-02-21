# Todo: Investigate F765/H743 Arming Lockup

## Phase 1: Code Analysis

- [x] Find and review F765 blackbox changes in 8.0.0
  - [x] `git log --oneline v7.1.2..v8.0.0 -- src/main/blackbox/`
  - [x] `git log --oneline v7.1.2..v8.0.0 -- src/main/drivers/sdcard/`
  - [x] Review each commit for potential race conditions
  - **Finding:** Commit `3561feeb9` rewrote F7 SDIO driver to use HAL
- [x] Analyze arming sequence in `fc_core.c`
  - [x] What initializes when ARMING_FLAG is set?
  - [x] What blackbox operations start at arm?
  - [x] What GPS/nav operations change at arm?
  - **Finding:** blackboxStart() called at line 894, triggers SD card access
- [x] Map DMA channels on F765
  - [x] Which DMA streams used for SD card?
  - [x] Which DMA streams used for PWM/servo?
  - [x] Which DMA streams used for UART (GPS)?
  - [x] Any shared DMA controllers?
  - **Finding:** SD DMA priority LOW, can be starved by other operations
- [x] Review interrupt priorities
  - [x] Check NVIC priorities for SD, PWM, GPS
  - [x] Look for priority inversion risks
  - **Finding:** SDMMC interrupt priority 2

## Phase 2: Identify Critical Code Paths

- [x] Trace arming code path
  - [x] `tryArm()` function
  - [x] `ENABLE_ARMING_FLAG(ARMED)` effects
  - [x] Motor/servo output activation
- [x] Trace blackbox arm behavior
  - [x] When does logging actually start?
  - [x] SD card write initiation
  - [x] Buffer allocation/initialization
  - **Finding:** blackboxStart() → blackboxDeviceOpen() → AFATFS needs SD
- [x] Trace GPS fix handling
  - [x] What happens when `STATE(GPS_FIX)` becomes true?
  - [x] AHRS reconfiguration at fix
  - [x] Navigation state changes
  - **Finding:** GPS fix triggers DMA activity, can put SD in error state
- [x] Identify shared resources
  - [x] Global locks or mutexes
  - [x] Shared buffers
  - [x] DMA completion flags
  - **Finding:** Blocking reset loop with `goto doMore` pattern

## Phase 3: Specific Checks

- [x] Check for blocking operations at arm time
  - [x] SD card sync operations?
  - [x] Flash writes?
  - [x] Config saves?
  - **Finding:** HAL_SD_Init() is BLOCKING (up to 100s of ms)
- [x] Check for interrupt disable periods
  - [x] Critical sections in arming?
  - [x] DMA interrupt handling?
- [x] Check timing assumptions
  - [x] Hard-coded delays?
  - [x] Timeout handling?
  - [x] Busy-wait loops?
  - **Finding:** `sdcardSdio_reset(); goto doMore;` creates busy-loop

## Phase 4: Related Issues Review

- [x] Read #11299 - Primary issue analyzed
- [x] Read #10586 - Matek F765 freezing at arm
- [ ] Read #10646 for additional clues
- [ ] Read #10659 for additional clues
- [ ] Read #10800 for additional clues
- [ ] Read #11007 (F765 in-flight lockup) for additional clues
- [x] Look for common patterns across all issues
  - **Finding:** All F7/H7, all since 8.0.0, all involve SD/blackbox

## Phase 5: Testing Strategy

- [ ] Define test matrix
  - [ ] With/without SD card
  - [ ] Different logging rates (off, 3%, 10%, 32%)
  - [ ] Different PWM protocols (Standard, Oneshot, Dshot)
  - [ ] Arm before/after GPS fix
- [ ] SITL testing plan (if applicable)
- [ ] Hardware testing plan (if F765 available)

## Phase 6: Documentation

- [x] Document findings in summary.md
- [x] Create timeline of relevant commits
- [x] Diagram DMA/interrupt interactions (freeze mechanism flow)
- [x] Propose fix or workaround
  - Option 1: Update STM32F7 HAL (V1.2.2 → V1.3.3)
  - Option 2: Code fixes (non-blocking reset, remove goto doMore)
  - Option 3: User workarounds documented

## Completion

- [x] Root cause identified or narrowed down
  - **Root cause:** Commit `3561feeb9` F7 SDIO HAL rewrite
  - **Mechanism:** Blocking HAL_SD_Init() + goto doMore loop
- [x] Findings documented
- [ ] Send completion report to manager
- [ ] Consider posting findings to GitHub issue
- [ ] Verify fix with HAL update (see update-stm32f7-hal project)

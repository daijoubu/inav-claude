# Task Assignment: Investigate F765/H743 Arming Lockup

**Date:** 2026-02-21 13:09 | **From:** Manager | **To:** Developer | **Priority:** HIGH

## Task
Investigate and resolve intermittent FC lockup/freeze occurring at arming time on F765 and H743 boards. This issue appeared in INAV 8.0.0 and did not exist in 7.1.2. Multiple users report complete system freeze requiring power cycle, affecting servo control, OSD, and telemetry.

## Project
**Project Directory:** `claude/projects/active/investigate-f765-arming-lockup/`

**Related Issues:** #11299, #10586, #10646, #10659, #10800, #11007

## Background

### Key Symptoms
- FC completely freezes at moment of arming
- Servos/motors unresponsive, OSD frozen, telemetry stops
- Intermittent failure (2-80% failure rate)
- Power cycle required to recover
- Servo jitter observed at GPS fix moment
- SD card corruption reported in some cases

### Hypotheses to Investigate
1. **Blackbox/SD card race condition** - Logging starts at arm, may trigger conflict
2. **DMA channel conflict** - Servo output, blackbox writing, and GPS UART may compete
3. **GPS/AHRS update at fix time** - Triggers resource contention
4. **Interrupt priority deadlock** - Specific to F765/H743 architecture

## What to Do

### Step 1: Code Analysis
1. Review F765 blackbox changes between 7.1.2 and 8.0.0
2. Analyze arming sequence code path in `fc_core.c`
3. Map DMA channel usage on F765/H743
4. Trace system state at arming moment (blackbox, GPS, servos)
5. Identify shared resources and potential race conditions
6. Review related issues for common patterns

### Step 2: Investigation Scope
**Key Files to Investigate:**
- `src/main/blackbox/blackbox.c`, `blackbox_io.c`
- `src/main/drivers/sdcard/sdmmc_sdio_*.c`
- `src/main/fc/fc_core.c` (arming logic)
- `src/main/drivers/dma_stm32f7xx.c`
- `src/main/drivers/pwm_output.c`

### Step 3: Documentation
- Document all findings
- Propose fix or workaround
- Prepare findings for posting to GitHub issues

## Success Criteria
- [ ] Root cause identified or significantly narrowed down
- [ ] Theory validated with code evidence
- [ ] Fix proposed or workaround documented
- [ ] Findings ready to post to GitHub issues
- [ ] Related issues reviewed for common patterns

## Effort Estimate
**8-16 hours**

---

**Manager**

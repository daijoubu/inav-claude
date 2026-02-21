# Project: Investigate F765/H743 Arming Lockup

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Investigation / Bug Analysis
**Created:** 2026-02-21
**Estimated Effort:** 8-16 hours

## Overview

Investigate intermittent FC lockup/freeze at arming time, primarily affecting F765 and H743 flight controllers. Multiple users have reported this issue since INAV 8.0.0, with the problem appearing to involve GPS fix timing, blackbox logging, and possibly DMA/interrupt conflicts.

## Related Issues

| Issue | Title | Hardware | Key Symptom |
|-------|-------|----------|-------------|
| #11299 | Outputs lockup after GPS fix at arming | H743, F765 | Servo jitter at GPS fix, then lockup |
| #10586 | Matek F765 freezing when arming | F765-WSE | 4/5 arm attempts freeze, SD corruption |
| #10646 | Random freeze after time | F7xx | Freeze after random duration |
| #10659 | F7 lockup | F7xx | Related lockup |
| #10800 | F7/H7 issue | F7/H7 | Related issue |
| #11007 | F765 lockup in flight | F765 | In-flight freeze |

## Problem Summary

**Symptoms:**
- FC completely freezes at moment of arming
- Servos/motors become unresponsive
- OSD frozen, telemetry stops
- No blackbox log created for failed arm
- Power cycle required to recover
- Intermittent: 2-80% failure rate depending on user

**Affected Hardware:**
- Matek F765-WSE (primary)
- Other F765 boards
- H743 boards (less frequent)
- NOT reported on F4xx or other MCUs

**Timeline:**
- Works fine in INAV 7.1.2
- Problem started in INAV 8.0.0
- Persists through 8.0.x and 9.0.x

**Potential Triggers:**
1. GPS 3D fix acquisition
2. Blackbox logging initialization
3. SD card operations
4. Arming sequence timing

## Hypotheses

### H1: Blackbox/SD Card Race Condition
Changes made to F765 blackbox logging in 8.0.0 may have introduced a race condition when blackbox starts at arming time, especially if GPS fix occurs simultaneously.

**Evidence:**
- SD card corruption reported
- No blackbox log for failed arms
- Problem appeared in 8.0.0 when F765 blackbox fixes were made
- One user reported freeze after SD card reformat

### H2: DMA Conflict at Arming
DMA channels for servo output, blackbox writing, and GPS UART may conflict at the critical moment when multiple systems activate at arming.

**Evidence:**
- Servo jitter at GPS fix (DMA activity)
- PWM outputs become unresponsive
- Linked to logging rate >3% with slower PWM (Standard, Oneshot125, Dshot150)

### H3: GPS/AHRS Update Triggers Issue
The AHRS update triggered by GPS fix may cause resource contention with other systems initializing at arm time.

**Evidence:**
- Servo jitter at exact moment of GPS fix
- Lockup often occurs when arming shortly after GPS fix
- User reports arming before GPS fix works around issue

### H4: Interrupt Priority/Deadlock
An interrupt priority issue specific to F765/H743 may cause deadlock when multiple high-priority interrupts fire simultaneously at arming.

**Evidence:**
- Complete FC freeze (not just output)
- Affects specific MCU families
- Intermittent timing-dependent behavior

## Investigation Plan

### Phase 1: Code Analysis
1. Review F765 blackbox changes in 8.0.0 (diff 7.1.2 → 8.0.0)
2. Analyze arming sequence code path
3. Map DMA channel usage on F765/H743
4. Review interrupt priorities for affected subsystems

### Phase 2: Identify Critical Code Paths
1. Trace what happens at arming moment
2. Identify all systems that initialize/activate at arm
3. Find shared resources (DMA, buffers, locks)
4. Look for potential race conditions

### Phase 3: SITL Analysis (if possible)
1. Attempt to reproduce timing in SITL
2. Add instrumentation to arming code
3. Test with simulated GPS fix timing

### Phase 4: Hardware Testing (if hardware available)
1. Test on F765 with various configurations
2. Test with/without SD card
3. Test with different logging rates
4. Test with different PWM protocols

## Success Criteria

- [ ] Root cause identified
- [ ] Theory validated with code evidence
- [ ] Fix proposed or workaround documented
- [ ] Findings reported to upstream

## Files to Investigate

**Blackbox:**
- `src/main/blackbox/blackbox.c`
- `src/main/blackbox/blackbox_io.c`
- `src/main/drivers/sdcard/sdmmc_sdio_*.c`

**Arming:**
- `src/main/fc/fc_core.c` (arming logic)
- `src/main/fc/runtime_config.c`

**DMA/PWM:**
- `src/main/drivers/dma_stm32f7xx.c`
- `src/main/drivers/pwm_output.c`
- `src/main/drivers/timer_stm32f7xx.c`

**GPS/Navigation:**
- `src/main/io/gps.c`
- `src/main/navigation/navigation.c`
- `src/main/flight/imu.c` (AHRS)

## References

- Issue #11299: https://github.com/iNavFlight/inav/issues/11299
- Issue #10586: https://github.com/iNavFlight/inav/issues/10586
- User CLI diff (10586): https://github.com/user-attachments/files/18388760/diff.txt
- User CLI diff (11299): https://github.com/user-attachments/files/24956264/INAV_9.0.0_cli.txt

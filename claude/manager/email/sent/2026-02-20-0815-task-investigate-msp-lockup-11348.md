# Task Assignment: Investigate MSP Lock-up (Issue #11348)

**Date:** 2026-02-20 08:15
**From:** Manager
**To:** Developer
**Project:** investigate-msp-lockup-11348
**Priority:** HIGH
**Estimated Effort:** 4-8 hours
**Branch:** From `maintenance-9.x`

## Task

Investigate a critical FC lock-up issue where the flight controller freezes completely when an MSP reader disconnects while LOG_DEBUG is active. Identify the root cause (suspected infinite loop in serial/MSP code) and document findings.

## Background

User reported losing 6 planes due to this bug. When using LOG_DEBUG statements and disconnecting the MSP reader:
- FC locks up completely (controls, telemetry stop)
- Motors continue at last commanded state
- Cannot disarm
- FC resumes normal operation when MSP reader reconnects

This behavior strongly indicates an infinite loop rather than a hard fault.

**Issue:** [#11348](https://github.com/iNavFlight/inav/issues/11348)
**Reporter:** mstrakl
**Affected Version:** 9.0.1
**Board:** MATEK F405 Wing V2

## What to Do

1. Search for infinite `while` loops in `src/main/io/msp_serial.c` and `src/main/drivers/serial.c`
2. Analyze LOG_DEBUG buffer handling (see `docs/development/serial_printf_debugging.md`)
3. Trace MSP disconnect code path - what happens when reader closes connection?
4. Identify race conditions or deadlock scenarios
5. Document root cause and propose fix approach

## Files to Check

- `src/main/io/msp_serial.c`
- `src/main/drivers/serial.c`
- `src/main/io/serial.c`
- `docs/development/serial_printf_debugging.md`

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Affected code paths mapped
- [ ] Proposed fix documented in summary.md
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/investigate-msp-lockup-11348/`

---
**Manager**

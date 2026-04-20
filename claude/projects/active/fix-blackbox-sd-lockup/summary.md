# Project: Fix Blackbox SD Card Lockup

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix / Safety Issue
**Created:** 2026-02-09
**Estimated Effort:** 4-8 hours

## Overview

A user reported that the flight controller completely locked up (no MSP or any other activity) when using a certain SD card for blackbox logging. The FC should never lock up due to a peripheral failure. Blackbox logging problems should result in only logging failing gracefully, not taking down the entire FC.

## Problem

- FC completely freezes when a problematic SD card is used for blackbox logging
- No MSP communication, no flight control — total lockup
- This is a safety hazard: loss of flight control due to a logging peripheral

## Solution

1. Audit error handling in blackbox SD card code paths for:
   - Blocking operations without timeouts
   - Missing error checks on SD card read/write/init
   - Infinite loops or retries without bounds
   - SPI/SDIO bus operations that could block indefinitely
2. Add proper timeouts, error handling, and graceful degradation
3. On blackbox failure, disable logging and continue normal FC operation
4. Bonus: Show OSD system message or similar indication when blackbox logging fails

## Success Criteria

- [ ] Identified the code path(s) that can cause FC lockup
- [ ] Added timeouts/error handling so SD card failures can't block the FC
- [ ] Blackbox logging fails gracefully — FC continues normal operation
- [ ] Bonus: Error indication shown to user (OSD message or similar) if small change
- [ ] Code compiles for SITL and at least one hardware target
- [ ] PR created against `maintenance-9.x`

## Related

- **Assignment:** `manager/email/sent/2026-02-09-task-fix-blackbox-sd-lockup.md`

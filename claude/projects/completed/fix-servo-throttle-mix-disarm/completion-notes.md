# Completion Notes

**Status:** COMPLETE
**Date:** 2026-02-09
**PR:** https://github.com/iNavFlight/inav/pull/11318
**Commit:** b4ca845cd
**Branch:** fix-servo-throttle-mix-disarm (based on maintenance-9.x)

## Fix Summary

Removed broken post-hoc servo override in `servos.c` that set `servo[target] = motorConfig()->mincommand` when disarmed (ignoring servo reversal and negative mixer weights). Replaced with pre-mixer input clamping that forces throttle inputs to -500 when disarmed, letting the full mixer pipeline compute correct safe positions.

## Test Results

5/5 SITL tests passing. CI tests and SITL builds all green. Hardware builds in progress.

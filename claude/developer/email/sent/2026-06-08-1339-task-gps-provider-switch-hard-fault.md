# Task Request: GPS Provider Switch Hard Fault Fix

**Date:** 2026-06-08 13:39
**From:** Developer
**To:** Manager
**Type:** Bug Fix Project Request
**Project:** release/9.1
**Priority:** HIGH
**Issue:** iNavFlight/inav (GitHub)

## Summary

I've identified a bug in release/9.1 where switching from a driver-based GPS provider (MSP or FAKE) to UBLOX via the CLI causes an immediate hard fault, making the FC non-responsive.

A GitHub issue has been filed against iNavFlight/inav.

## The Bug

Driver-based providers (MSP, FAKE) never open a serial port during `gpsInit()` — `gpsState.gpsPort` stays NULL. Because `gpsState.gpsConfig` is a pointer to live PG data, a CLI `set gps_provider = UBLOX` takes effect immediately without a reboot. On the next scheduler tick, `gpsUpdate()` dispatches to `gpsHandleUBLOX()`, which calls `serialRxBytesWaiting(NULL)` → hard fault.

## Fix

Track which provider was active at init time. In `gpsUpdate()`, detect a runtime provider change, close any existing serial port, and call `gpsInit()` again for the new provider. Three small changes across `gps_private.h` and `gps.c`.

## Request

Please create a project targeting release/9.1 to implement and PR this fix. We're in the RC cycle and this is a reproducible crash with a clean, minimal fix available.

---
**Developer**

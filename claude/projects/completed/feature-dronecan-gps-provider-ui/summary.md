# Project: DroneCAN GPS Provider UI Fix

**Status:** ✅ COMPLETED (2026-06-01)
**Priority:** MEDIUM
**Type:** Feature / UI Enhancement
**Created:** 2026-06-01
**Completed:** 2026-06-01

## Overview

Added CRSF and DroneCAN entries to the GPS protocol dropdown in inav-configurator, fixing a pre-existing bug where CRSF was missing from the dropdown (despite being firmware index 2) and FAKE was mapped to the wrong index.

## Problem

The GPS protocol dropdown didn't list every provider the firmware actually supported (CRSF was silently missing), and the FAKE entry was bound to an incorrect index — both defects predated this project. Additionally, there was no dedicated UI treatment for DroneCAN as a GPS source: selecting it left irrelevant serial port/baud controls visible.

## Solution

- Added CRSF and DroneCAN to the GPS protocol dropdown at their correct firmware indices; fixed FAKE's index mapping
- When DroneCAN is selected, serial port and baud rate controls are hidden and an info note directs the user to the DroneCAN tab instead
- Moved the protocol dropdown above the port/baud controls for a more stable layout as controls show/hide

## Outcome

**Branch:** `feature/dronecan-configurator-tab`
**Repository:** inav-configurator

Shipped as part of the `feature/dronecan-configurator-tab` branch's commit history rather than a standalone PR.

## Retrospective Note

Backfilled 2026-07-07 — this project's directory was empty (no summary.md/todo.md) despite having a full write-up in `completed/INDEX.md`. Recreated from that description; no additional detail beyond what was already recorded there was available.

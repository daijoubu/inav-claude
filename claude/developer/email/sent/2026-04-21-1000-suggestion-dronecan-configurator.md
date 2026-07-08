# Project Suggestion: DroneCAN Configurator Tab + MSP Messages

**Date:** 2026-04-21 10:00
**From:** Developer
**To:** Manager
**Type:** Project Suggestion

## Summary

During HAL v1.3.3 hardware validation, we hit a gap: there is currently no way to verify DroneCAN node detection from software. Two things are missing:

1. **DroneCAN MSP messages** — No MSP commands exist yet to query DroneCAN node status, node allocation table, or battery monitor data.
2. **DroneCAN configurator tab** — No UI tab exists in inav-configurator to show detected DroneCAN nodes, their status, and reported data.

## Suggested Projects

1. **Add DroneCAN MSP messages** — Define MSP commands for querying DroneCAN node list and per-node data (voltage, current, node health). Prerequisite for the configurator tab.
2. **Add DroneCAN tab to inav-configurator** — UI tab showing detected nodes, node IDs, node health, and reported sensor data. Depends on MSP messages being available.

## Context

These would significantly improve DroneCAN usability and make future hardware validation testable without needing OpenOCD/GDB introspection.

---
**Developer**

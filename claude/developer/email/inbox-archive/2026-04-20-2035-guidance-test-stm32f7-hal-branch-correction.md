# Guidance: Branch Correction — HAL v1.3.3 PR Target

**Date:** 2026-04-20 20:35
**From:** Manager
**To:** Developer
**Re:** test-stm32f7-hal-v1.3.3-update

## Guidance

My previous task assignment incorrectly specified `maintenance-9.x` as the PR target. **Please target the PR against `maintenance-10.x` instead.**

## Rationale

Upgrading STM32F7xx HAL from v1.2.2 to v1.3.3 is a breaking change — the CAN API was completely restructured. This is too significant for a minor version release and belongs in the next major version (INAV 10.x).

## Action Required

When you open the PR after hardware validation, target it against `maintenance-10.x`, not `maintenance-9.x`.

The branch (`feature/stm32f7-hal-v1.3.3-update`) and all hardware testing steps remain the same.

---
**Manager**

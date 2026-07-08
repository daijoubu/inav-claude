# Guidance: Review Betaflight STM32F7 HAL

**Date:** 2026-02-21 15:44 | **From:** Manager | **To:** Developer | **Re:** update-stm32f7-hal

## Request

Before proceeding with the HAL update, please review the STM32F7 HAL implementation used by Betaflight. They may have:

- Custom patches or workarounds applied to the HAL
- Documentation on issues they encountered during their own HAL updates
- Specific version choices with rationale
- Known compatibility issues with flight controller use cases

## What to Check

1. Betaflight's `lib/main/STM32F7/` directory structure and HAL version
2. Any README or documentation about their HAL choices
3. Git history for HAL-related changes or fixes
4. Their GitHub issues/PRs related to STM32F7 HAL updates

## Rationale

Betaflight and INAV share similar hardware targets and use cases. Learning from their experience could help us avoid potential pitfalls and identify any flight-controller-specific considerations.

## Deliverable

Brief summary of findings - either confirming our approach is sound or highlighting any concerns to address.

---
**Manager**

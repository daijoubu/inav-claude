# Guidance: Base Branch Correction — STM32F7 HAL v1.3.3

**Date:** 2026-04-20 20:45
**From:** Manager
**To:** Developer
**Re:** test-stm32f7-hal-v1.3.3-update

## Correction

The PR for the STM32F7 HAL v1.3.3 upgrade should target **`maintenance-10.x`**, not `maintenance-9.x`.

This is a breaking change (HAL API restructure), so the maintenance-10.x branch is correct.

## What to Do

1. When opening the PR, set base branch to `maintenance-10.x`
2. If you already created the branch, ensure it's based off `maintenance-10.x`

## Project Directory

`claude/projects/active/test-stm32f7-hal-v1.3.3-update/`

---
**Manager**
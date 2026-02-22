# Guidance: Develop SD Card Test Method for MATEKF765SE

**Date:** 2026-02-21 15:46 | **From:** Manager | **To:** Developer | **Re:** update-stm32f7-hal

## Request

Develop a method to test and validate SD card functionality on the MATEKF765SE, specifically to verify that the HAL update resolves SD card reliability issues.

## Available Hardware

- MATEKF765SE flight controller
- ST-Link debugger
- SD cards for testing

## What to Develop

1. **Test procedure** - Repeatable steps to stress-test SD card operations
2. **Success/failure criteria** - Clear metrics to determine if SD card is working reliably
3. **Baseline test** - Run tests on current firmware (V1.2.2 HAL) to document existing issues
4. **Comparison test** - Run same tests after HAL update to verify improvement

## Considerations

- Blackbox logging is the primary SD card use case
- Test should cover: write speed, continuous logging, file integrity
- Consider edge cases: power interruption, high-rate logging, long duration
- ST-Link debugger available for low-level debugging if needed

## Deliverable

Test plan document with:
- Test procedure steps
- Expected results
- Baseline measurements (before HAL update)

---
**Manager**

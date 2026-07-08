# Guidance: Unit Testing for HAL Update

**Date:** 2026-04-13
**From:** Manager
**To:** Developer
**Re:** update-stm32f7-hal - unit testing feasibility

## Question

Would adding targeted unit tests for the STM32F7 HAL update provide meaningful confidence in the change? Or is the HAL too tightly coupled to hardware that unit tests cannot help?

## Context

Current unit test coverage in INAV focuses on high-level application logic (navigation, flight control, RC, OSD, sensors). HAL drivers (UART, I2C, SPI, SDIO, USB, DMA, interrupts) are not covered by existing unit tests.

The HAL update targets:
1. SD card reliability (primary lockup fix)
2. I2C transmission stalls
3. UART DMA race conditions
4. USB handling

## What to Investigate

1. **Feasibility:** Can HAL functions be tested in isolation with mocks?
2. **Value:** Would such tests catch regressions from the v1.2.2 → v1.3.3 upgrade?
3. **Scope:** What specific HAL areas would be testable vs. requiring hardware validation?

## Recommendation Needed

Please assess whether unit testing investment would add value, or if we should rely on build verification + hardware testing (HITL) for this update.

---

**Manager**
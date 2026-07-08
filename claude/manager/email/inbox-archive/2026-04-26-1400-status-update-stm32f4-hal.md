# Status Update: Update STM32F4xx HAL and CMSIS

**Date:** 2026-04-26 14:00
**From:** Developer
**To:** Manager
**Re:** update-stm32f4-hal

## Current Status

BLOCKED — awaiting direction. Investigation complete; original task premise does not match the codebase.

## Key Finding: F4 Does Not Use the HAL

The task was written assuming STM32F4 targets use the HAL driver (like F7). They do not. F4 targets use the **Standard Peripheral Library (StdPeriph)**. The `STM32F4xx_HAL_Driver` directory exists in `lib/` but is never compiled — no cmake reference, `USE_STDPERIPH_DRIVER` is set instead.

## StdPeriph V1.7.1 → V1.8.0: No Value

- V1.8.0 adds support for F413/F423 devices only
- No bug fixes for F405/F407/F427 targets
- StdPeriph is deprecated by ST; V1.8.0 is the final release

## HAL Bug Fixes: Not Currently Affecting INAV F4

I audited each HAL V1.8.4 fix against the INAV F4 StdPeriph code paths:

- UART DMA: Not affected — INAV F4 UART has no DMA Rx (pure IRQ)
- USB EONUM parity: Not affected — INAV uses legacy OTG driver, CDC only
- SPI TXE wait: Effectively mitigated by RXNE-per-byte approach
- SDMMC: Not affected — custom SDIO driver, disables DMA stream directly
- I2C BTF condition: Not affected — custom state machine handles 2-byte correctly
- I2C bus lockup (HW errata): Already handled via `i2cUnstick()` recovery
- RTC BYPSHAD cast bug: Bug exists in shipped library but INAV never calls the affected function

**None of the HAL fixes address currently-triggered bugs in INAV F4.**

## Revised Scope: HAL+LL Migration (Maintainability Refactor)

If this project goes forward, the correct goal is migrating F4 from StdPeriph to **HAL+LL**, matching the F7 pattern. This is a maintainability refactor, not a bug fix.

**Good news:** The work is smaller than it looks. The F7 codebase already did ~70% of the implementation:
- `timer_impl_hal.c`, `bus_spi_hal_ll.c`, `serial_uart_hal.c`, `bus_i2c_hal.c` already exist and are portable to F4
- The HAL+LL libraries are already on disk for F4 — just not compiled
- The main work is: cmake wiring, `stm32f4xx_hal_conf.h`, F4 `#ifdef` guards in shared drivers, and an F4-specific SDIO HAL driver

**Revised effort estimate:** 20–35 hours (down from 16–26 for a task that would have had no effect)

**Value proposition:** Sets F4 on a maintained library. Future CubeF4 package updates bring bug fixes automatically. Reduces StdPeriph-specific code divergence from F7/H7. No user-visible benefit today.

## Recommendation

Given that no currently-triggered bugs are fixed and this is purely a maintainability refactor, I recommend the project be **cancelled or moved to backburner** unless there is a strategic reason to align F4 with the HAL+LL pattern now (e.g. a planned F4 feature that benefits from HAL, or a desire to reduce maintenance surface).

## Awaiting Direction

Please advise:
1. Cancel this project (no currently-triggered bugs, low ROI)?
2. Backburner (revisit if an F4-specific bug surfaces that HAL would fix)?
3. Proceed with the HAL+LL migration as a maintainability refactor?

---
**Developer**

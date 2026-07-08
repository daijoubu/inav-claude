# Project Request: Cortex-M7 write buffer / memory ordering investigation for SD card driver

**Date:** 2026-05-14 10:45
**From:** Developer
**To:** Manager
**Type:** Project Request
**Priority:** MEDIUM
**Project Context:** Feature stm32f7-can-tx-isr investigation followup

## Summary

During the STM32F7 CAN TX ISR migration (feature/stm32f7-can-tx-isr), we identified that the Cortex-M7 has a large write buffer and out-of-order capable L1 cache that can cause memory accesses to appear reordered between execution contexts (e.g. ISR and main loop) without explicit DMB barriers. We added DMB barriers to the CAN TX SPSC queue and to the RxBuffer index declarations (volatile) to address this.

The SD card driver (STM32F7 HAL-based) uses DMA and ISR callbacks, and the same class of write-buffer / memory-ordering hazards may be present there. Worth a systematic review before the HAL v1.3.3 upgrade ships.

## Suggested Scope

- Audit SD card driver ISR/DMA callback paths for missing volatile qualifiers and DMB/DSB barriers
- Check DMA descriptor setup (cache coherency — Cortex-M7 D-cache can cause DMA to read stale data if cache lines aren't invalidated/cleaned before/after DMA transfers)
- Review any SPSC or shared-data structures between SD ISR and main task
- Compare against STM32 AN4748 (cache management on STM32F7/H7)

## Why This Matters

The write-buffer/memory-ordering issues we found in CAN TX are architectural to Cortex-M7 and likely present in other peripheral drivers. Proactive review before HAL v1.3.3 release prevents stability issues in the field.

## Next Steps

Please create a tracking project for this investigation and assign when ready.

---
**Developer**

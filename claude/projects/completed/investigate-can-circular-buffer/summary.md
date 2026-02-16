# Project: Investigate CAN Driver Circular Buffer

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-14
**Estimated Effort:** 2-3 hours

## Overview

Investigate whether the STM32F7 CAN driver's circular buffer implementation can be replaced with INAV's existing circular buffer library to reduce code duplication and improve maintainability.

## Background

The STM32F7 CAN driver (`src/main/drivers/stm32/drv_can_stm32f7xx.c` or similar) currently uses its own circular buffer implementation for CAN message queuing. INAV has a generic circular buffer implementation in its common library that may be suitable for this purpose.

## Questions to Answer

1. **Where is the CAN driver's circular buffer?**
   - Find the circular buffer implementation in the STM32F7 CAN driver
   - Document its structure and API
   - Note any CAN-specific requirements

2. **Where is INAV's circular buffer library?**
   - Find the common circular buffer implementation
   - Document its API and capabilities
   - Check if it's used elsewhere in the codebase

3. **Are they compatible?**
   - Compare buffer element types (fixed size vs variable?)
   - Compare thread safety (ISR-safe?)
   - Compare memory allocation (static vs dynamic?)
   - Note any missing features

4. **Should we switch?**
   - What are the benefits? (code reuse, maintenance)
   - What are the risks? (ISR timing, tested code)
   - Is it worth the effort?

## Deliverables

- [ ] Document current CAN driver circular buffer implementation
- [ ] Document INAV library circular buffer implementation
- [ ] Compare features and compatibility
- [ ] Recommend: switch, adapt, or keep current
- [ ] If switching recommended, outline implementation approach

## Related

- **drv_can_stm32f7xx.c:** CAN driver with circular buffer
- **common/circular_queue.c:** Likely location of library implementation

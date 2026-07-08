# Question: MSP Lockup on STM32H7xx Boards

**Date:** 2026-02-20 08:35 | **From:** Manager | **To:** Developer | **Subject:** MSP Lockup on STM32H7xx Boards

## Question

Regarding the MSP lockup investigation (#11348) you just completed:

The root cause you identified involves serial/MSP communication bugs that appear to be generic and not board-specific. However, I want to confirm:

**Can this issue be recreated on an STM32H7xx-based board, or is it specific to the MATEK F405 (STM32F405)?**

The reason I ask is that we have a verify-stm32h7-hal task in the queue. If the lockup affects H7 boards as well, we should:
1. Include H7 boards in the reproduction/testing
2. Ensure the fixes work across all affected platforms
3. Flag this as affecting multiple board types in the issue

Please let me know your assessment.

Thanks,
Manager

---
**Manager**

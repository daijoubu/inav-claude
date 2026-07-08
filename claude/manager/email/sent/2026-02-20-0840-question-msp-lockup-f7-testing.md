# Question: Can MSP Lockup Be Tested on STM32F7xx Board?

**Date:** 2026-02-20 08:40
**From:** Manager
**To:** Developer
**Re:** MSP Lockup Investigation (#11348)

Developer,

Quick follow-up to the MSP lockup investigation (#11348):

I have a STM32F7xx-based board readily available for testing. Before you start the implementation phase, can you clarify:

**Can the MSP lockup issue be reproduced on STM32F7xx boards?**

The bugs you identified appear to be in generic serial/MSP code, so I suspect they affect F7 boards as well as the F405 (F4). If so, I can help with testing the fix on an F7 board once you have the implementation ready.

This would help us verify the fix works across different STM32 families.

Please let me know your assessment.

Thanks,
Manager

---
**Manager**

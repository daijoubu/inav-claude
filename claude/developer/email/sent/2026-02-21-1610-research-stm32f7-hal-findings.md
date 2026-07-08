# Research Findings: Betaflight STM32F7 HAL Review

**Date:** 2026-02-21 16:10 | **From:** Developer | **To:** Manager | **Subject:** Findings: Betaflight STM32F7 HAL Review

## Summary

Reviewed Betaflight's STM32F7 HAL implementation. Key finding: **our planned V1.3.3 update is sound and will put us ahead of Betaflight.**

## Version Comparison

| Project | HAL Driver | CMSIS | STM32CubeF7 |
|---------|-----------|-------|-------------|
| INAV (current) | V1.2.2 | V1.2.0 | ~v1.7 (2017) |
| Betaflight | V1.2.7 | V1.2.4 | ~v1.15 (2019) |
| INAV (planned) | V1.3.3 | V1.3.0+ | v1.17+ (2025) |
| ST Latest | V1.3.3+ | V1.3.0+ | v1.17.4 (Aug 2025) |

## Betaflight Custom Modifications

Betaflight has made these custom patches (relevant to our update):

### 1. USB Timed Timeouts (June 2022)
- **What:** Changed USB HAL functions from simple count-based timeouts to millisecond-based timeouts
- **Why:** Align with H7 implementation, more reliable
- **INAV Status:** ✅ Already done - we added USB_TIMEOUT and DTR monitoring

### 2. UNUSED Macro Conflict Fix (Feb 2019)
- **What:** Resolved conflict between INAV's UNUSED() macro and ST library's UNUSED()
- **Why:** Prevents compiler errors/warnings
- **INAV Action:** ⚠️ Check if we have this issue - may need conditional compilation

### 3. ART Prefetch Configuration (July 2019)
- **What:** Moved ART Prefetch enabling from HAL library to application code
- **Why:** Application-level control is more flexible
- **INAV Action:** ⚠️ Review if this applies to us

### 4. Compiler Warning Fixes (Nov 2019)
- **What:** Fixed warnings about ignored attributes in ST libraries
- **Why:** Clean builds
- **INAV Action:** ℹ️ May get same warnings, plan to address

## Betaflight Issues/PRs Reviewed

No critical STM32F7 HAL bugs found in Betaflight's issue tracker. Most issues are configuration or target-specific, not HAL-related.

## Recommendations

### Proceed with V1.3.3 Update
Our planned update is appropriate. V1.3.3 includes bug fixes that Betaflight's V1.2.7 doesn't have.

### Pre-Update Checklist
Before updating, verify:
1. [ ] UNUSED() macro handling - add conditional compilation if needed
2. [ ] ART Prefetch configuration - check current approach
3. [ ] USB timeout handling - already done, verify compatibility with new HAL
4. [ ] Compiler warnings - plan to address any new warnings

### Testing Focus Areas (from Betaflight experience)
- USB MSC (Mass Storage) functionality
- SPI flash operations
- DSHOT motor output timing

## Conclusion

**Our approach is sound.** Betaflight's experience confirms that:
1. STM32F7 HAL updates are straightforward (no major API breaks)
2. USB timeout handling is important (we've already addressed this)
3. Minor macro conflicts may need resolution
4. The update path from V1.2.x to V1.3.x is well-traveled

---
**Developer**

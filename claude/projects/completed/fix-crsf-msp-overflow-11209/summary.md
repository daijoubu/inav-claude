# Project: Fix CRSF MSP Integer Overflow (#11209)

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix (Security)
**Created:** 2026-02-11
**Estimated Effort:** 1-2 hours

## Overview

Fix an integer overflow vulnerability in CRSF MSP handling that can cause out-of-bounds memory writes.

## Problem

In `crsfDataReceive()`, when handling `CRSF_FRAMETYPE_MSP_REQ` or `CRSF_FRAMETYPE_MSP_WRITE`, if `frameLength` is 3, the subtraction `frameLength - 4` underflows (becomes 0xFFFFFFFF as unsigned). This value is passed to `bufferCrsfMspFrame()` which does a `memcpy` with this massive length, causing out-of-bounds writes.

**Security Impact:** Out-of-bounds write vulnerability. A malformed CRSF frame could potentially crash the flight controller or cause undefined behavior.

## Solution

Add bounds check before the subtraction to discard malformed frames:

```c
if (crsfFrame.frame.frameLength < 4) {
    break;  // Discard malformed frame
}
```

## Files Affected

- `src/main/rx/crsf.c` - `crsfDataReceive()` function

## Success Criteria

- [ ] Bounds check added before `frameLength - 4` subtraction
- [ ] Malformed frames with length < 4 are safely discarded
- [ ] Existing CRSF MSP functionality still works (no regression)
- [ ] Code compiles without warnings
- [ ] Unit test added for edge case (if test infrastructure exists)
- [ ] PR created targeting maintenance-9.x

## References

- **Issue:** https://github.com/iNavFlight/inav/issues/11209
- **File:** `src/main/rx/crsf.c`

## Notes

This is a straightforward one-line fix with clear problem and solution documented in the issue. Reporter provided exact code location and suggested fix.

# Task Assignment: Fix CRSF MSP Integer Overflow (#11209)

**Date:** 2026-02-11 09:02
**From:** Manager
**To:** Developer
**Project:** fix-crsf-msp-overflow-11209
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

Fix an integer overflow vulnerability in CRSF MSP handling that can cause out-of-bounds memory writes. This is a security issue.

## Background

In `crsfDataReceive()`, when handling `CRSF_FRAMETYPE_MSP_REQ` or `CRSF_FRAMETYPE_MSP_WRITE`, if `frameLength` is 3, the subtraction `frameLength - 4` underflows (becomes 0xFFFFFFFF as unsigned). This value is passed to `bufferCrsfMspFrame()` which does a `memcpy` with this massive length, causing out-of-bounds writes.

## What to Do

1. Read issue #11209 for full context
2. Locate `crsfDataReceive()` in `src/main/rx/crsf.c`
3. Add bounds check before the subtraction:
   ```c
   if (crsfFrame.frame.frameLength < 4) {
       break;  // Discard malformed frame
   }
   ```
4. Ensure both MSP_REQ and MSP_WRITE cases are protected
5. Build and test
6. Create PR targeting maintenance-9.x

## Success Criteria

- [ ] Bounds check added before `frameLength - 4` subtraction
- [ ] Malformed frames with length < 4 are safely discarded
- [ ] Existing CRSF MSP functionality still works (no regression)
- [ ] Code compiles without warnings
- [ ] PR created targeting maintenance-9.x

## Files Affected

- `src/main/rx/crsf.c` - `crsfDataReceive()` function

## References

- Issue: https://github.com/iNavFlight/inav/issues/11209

## Project Directory

`claude/projects/active/fix-crsf-msp-overflow-11209/`

## Notes

This is a straightforward one-line fix. The reporter provided exact code location and suggested fix. High priority due to security implications (out-of-bounds write vulnerability).

---
**Manager**

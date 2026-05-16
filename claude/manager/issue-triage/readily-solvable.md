# Readily Solvable Issues

Issues with clear problems, known solutions, and reasonable effort to fix.

## Criteria

- Clear reproduction steps
- Isolated, specific problem
- No special hardware required
- Community consensus on expected behavior
- Small to moderate code changes

---

## Issues

### ~~#11209 - Integer overflow in CRSF MSP handling~~ FIXED

**Status:** CLOSED - Fixed via PR #11210 (merged)
**URL:** https://github.com/iNavFlight/inav/issues/11209

~~Security issue (OOB write) in CRSF MSP handling.~~

**Resolution:** Already fixed in maintenance-9.x. Bounds check added at `src/main/rx/crsf.c:181`.

---

### #10674 - SPI busWriteBuf uses wrong register masking

**Created:** 2025-02-06
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/10674

**Problem:**
In `busWriteBuf()`, for SPI devices, the code uses `reg | 0x80` (sets MSB for read) but should use `reg & 0x7F` (clears MSB for write). Compare with `busWrite()` which correctly uses `reg & 0x7F`.

Current (wrong):
```c
return spiBusWriteBuffer(dev, reg | 0x80, data, length);  // Line 286
```

Should be:
```c
return spiBusWriteBuffer(dev, reg & 0x7F, data, length);
```

**Files Affected:**
- `src/main/drivers/bus.c` line 286

**Notes:**
Clear bug with one-line fix. Reporter shows side-by-side comparison with correct `busWrite()` function. Bug has existed since at least INAV 3.0.0.

---

### #10660 - Climb rate deadband applied twice

**Created:** 2025-01-30
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav/issues/10660

**Problem:**
Manual climb rate doesn't match configurator setting because deadband is applied twice:
1. First at line 140: `rcCommand = applyDeadbandRescaled(...)`
2. Again at lines 149 and 153 which call functions using the original rcCommand

**Proposed Solution:**
Reorder the code so `applyDeadbandRescaled` is called after the neutral point calculation instead of before. Reporter provides tested fix:
```c
// Move deadband application after the -500/500 adjustment
rcCommand = rcCommand - 500;
rcCommand = applyDeadbandRescaled(rcCommand, ...);
```

**Files Affected:**
- `src/main/navigation/navigation_multicopter.c` lines 140-153

**Notes:**
Reporter has tested the fix and confirms it works. Bug has existed since at least INAV 3.0.0.

<!-- Template for adding issues:

### #XXXXX - Issue Title

**Created:** YYYY-MM-DD
**Labels:** bug, etc
**URL:** https://github.com/iNavFlight/inav/issues/XXXXX

**Problem:**
Brief description of the issue.

**Proposed Solution:**
What needs to be done to fix it.

**Files Likely Affected:**
- `src/main/path/to/file.c`

**Notes:**
Any additional context.

**Assigned:** (project name if assigned)

-->

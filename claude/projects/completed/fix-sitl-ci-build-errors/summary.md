# Project: Fix SITL CI Build Errors on PR #11313

**Status:** ✅ COMPLETED
**Priority:** HIGH
**Type:** Bug Fix / CI
**Created:** 2026-02-13
**Completed:** 2026-02-14
**Effort:** ~3 hours

## Overview

Fixed CI build failures in PR #11313 (DroneCAN SITL implementation) on macOS and Windows platforms.

## Problem

PR #11313 had unguarded SocketCAN function forward declarations in canard_sitl_driver.c. On macOS and Windows:
- The forward declarations existed but implementations were inside `#ifdef __linux__` blocks
- This caused "unused function" compiler warnings
- With `-Werror`, these warnings became fatal errors

## Solution

**Root Cause:** SocketCAN functions were forward-declared unconditionally but only implemented inside `#ifdef __linux__` blocks, causing "unused function" warnings on non-Linux platforms.

**Fix:** Guard the SocketCAN forward declarations (lines 51-57 of canard_sitl_driver.c) with `#ifdef __linux__`:
- Stub function declarations remain always visible (used on all platforms)
- SocketCAN declarations only visible on Linux (where implemented)
- Eliminates unused function warnings on macOS/Windows

**Approach:** Did NOT guard the socket.h include in target.h - macOS and Windows have POSIX socket support and need the socket functions.

## Success Criteria

- [x] Identify root cause of Windows SITL build error
- [x] Identify root cause of macOS SITL build error
- [x] Fix Windows SITL build
- [x] Fix macOS SITL build
- [x] All CI checks pass
- [x] Code compiles cleanly
- [x] No functional regressions

## Results

**All SITL CI builds passing:**
- ✓ Linux SITL: 40s
- ✓ macOS SITL: 1m18s
- ✓ Windows SITL: 3m39s
- ✓ Linux ARM64 SITL: 42s
- ✓ Unit Tests: 56s

**Commits:**
1. `dc287d1d3` - Revert incorrect socket.h guards
2. `0664cff54` - Guard SocketCAN forward declarations (the correct fix)

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313) - Ready for maintainer merge
- **Related Project:** dronecan-sitl-implementation (completed)
- **Related Project:** pr-11313-build-fixes (completed)

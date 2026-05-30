# Project: Add ArduPilot Fork as Submodule + Build ctags Index

**Status:** 🚧 IN PROGRESS
**Priority:** MEDIUM
**Type:** Infrastructure / Tooling
**Created:** 2026-05-26
**Estimated Effort:** 2-4 hours (mostly waiting on clone + indexing)

## Overview

Add the user's ArduPilot fork (`daijoubu/ardupilot`) as a git submodule of `inav-claude`, then build a ctags symbol index for fast cross-referencing against INAV's DroneCAN/CAN code.

Also fixes pre-existing broken `.gitmodules` — both `inav` and `inav-configurator` are tracked in the git index as submodules (gitlinks) but have no `.gitmodules` mapping entry.

## Problem

- No `.gitmodules` file exists despite `inav` and `inav-configurator` being committed as submodule gitlinks
- Need to cross-reference ArduPilot's CAN driver code with INAV's for the DroneCAN investigation
- Manual `grep` across repos is slow without a shared symbol index

## Solution

ArduPilot kept as a local clone (not a git submodule) and gitignored, matching the pattern used for inav/inav-configurator. ctags index built locally at `ArduPilot/tags`.

**Regenerate index:**
```bash
cd ArduPilot && ctags -R --fields=+niazS --extras=+q --exclude=.git --exclude=build --exclude=tools --exclude=modules -f tags .
```

## Success Criteria

- [x] ArduPilot cloned at `ArduPilot/`
- [x] ArduPilot added to `.gitignore`
- [x] ctags index built (`ArduPilot/tags`, 177k entries)
- [x] Regeneration steps documented above

## Related

- **ArduPilot fork:** https://github.com/daijoubu/ardupilot
- **Repository:** inav-claude
- **Pauses:** `active/investigate-dronecan-reboot-gps` (temporarily paused for this infra work)

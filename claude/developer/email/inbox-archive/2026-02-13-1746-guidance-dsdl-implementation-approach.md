# Guidance: DSDL Implementation Approach - Recommended Path

**Date:** 2026-02-13 17:46
**From:** Manager
**To:** Developer
**Re:** DroneCAN SITL Phase 2 - DSDL File Organization

## Guidance

Thank you for the excellent research and documentation. Your DSDL-GUIDE.md is comprehensive and will be valuable for future maintenance.

**Keep the current strategy: Commit all DSDL files to the repository.** Do NOT pursue git submodules.

## Rationale

1. **INAV avoids submodules** - Historically problematic for contributor UX and CI/CD
2. **DSDL rarely changes** - Last update was 2026-01-24; not a fast-moving dependency
3. **All 119 files actively compiled** - No unused code to worry about
4. **Deterministic naming** - You documented that naming convention is deterministic (e.g., uavcan.equipment.power.BatteryInfo → uavcan_equipment_power_BatteryInfo), which means developers can add messages without regenerating
5. **Current state is acceptable** - Having committed DSDL code is standard practice for firmware projects

## When to Revisit

Only pursue alternatives if:
- DSDL updates become frequent (>quarterly)
- File size becomes a blocker (unlikely at 257 files)
- New developers consistently request automated updates

## Implementation For This Project

**Phase 2: File Organization (Next)**

Since all 119 files are actively compiled, the reorganization goal should be:
- Document where DSDL files live and why
- Document the process if/when they need updating (regeneration steps)
- Keep the current committed structure (no reorganization needed)

**Success for this project:** Document is complete (DSDL-GUIDE.md), no code changes required.

## Next Steps

1. Archive this as decision documentation
2. Transition Phase 2 to documentation/process work (not code reorganization)
3. Consider minimal scope: Update README to point to DSDL-GUIDE.md

---
**Manager**

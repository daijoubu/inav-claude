# Project: Document Parameter Group System

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Documentation
**Created:** 2026-01-22
**Estimated Effort:** 4-6 hours

## Overview

Create comprehensive documentation of INAV's parameter group (PG) system, explaining how configuration settings are registered, versioned, stored, and loaded. This includes documenting the `__pg_registry_*` linker sections, the version increment rules, and the relationship to settings.yaml.

## Problem

The parameter group system is complex and undocumented. Developers need to understand:
- When and why to increment PG versions
- How the registry macros work
- How settings.yaml relates to parameter groups
- What happens when versions mismatch

A recent PR #11236 highlighted this issue when a maintainer noted that removing a struct field requires incrementing the PG version, or "settings will be broken after flashing."

## Solution

Create detailed documentation in `claude/developer/docs/parameter_groups/` covering:

1. **Overview**: What parameter groups are and why they exist
2. **Registration Macros**: PG_REGISTER, PG_REGISTER_WITH_RESET_TEMPLATE, etc.
3. **Versioning Rules**: When and why to increment the version number
4. **The Registry**: How `__pg_registry_start` and `__pg_registry_end` work
5. **Storage & Loading**: How settings are persisted and validated
6. **settings.yaml Relationship**: How YAML settings map to PG structs
7. **Case Study**: PR #11236 blackbox example

## Implementation

### Phase 1: Research & Understanding (2-3 hours)

1. Study `src/main/config/parameter_group.h`
2. Examine several PG registration examples:
   - `blackbox.c` (system config with reset template)
   - Other examples of profile configs
3. Trace through the version checking in pgLoad()
4. Review PR #11236 changes and Pawel's comment
5. Check existing documentation in `inav/docs/development/`

### Phase 2: Documentation (2-3 hours)

Create the following files in `claude/developer/docs/parameter_groups/`:

1. **README.md** - Main overview document
2. **versioning-rules.md** - When to increment versions
3. **registration-guide.md** - How to use PG macros
4. **case-study-pr11236.md** - The blackbox example

**Key Topics to Cover:**

**Version Increment Rules:**
- Increment when adding/removing struct fields
- Increment when changing field types
- Increment when changing field order
- Why: pgLoad() validates version compatibility
- **Version Limits:** 4-bit field (0-15), wraps from 15→0
- **Wraparound Handling:** What happens when version wraps to 0

**The Registry Mechanism:**
- Linker sections `.pg_registry` and `.pg_resetdata`
- How macros populate these sections at compile time
- How `PG_FOREACH` iterates the registry
- Version stored in top 4 bits of pgn field (line 45, 57)
- Version range: 0-15 (4 bits)
- Version extraction: `(pgn >> 12) & 0xF`

**settings.yaml Connection:**
- Settings map to struct fields
- Type checking and bounds
- Default values come from PG_RESET_TEMPLATE

**PR #11236 Case Study:**
```c
// Before: blackboxConfig_t had invertedCardDetection field
typedef struct blackboxConfig_s {
    uint16_t rate_num;
    uint16_t rate_denom;
    uint8_t device;
    uint8_t invertedCardDetection;  // <-- REMOVED
    uint32_t includeFlags;
    int8_t arm_control;
} blackboxConfig_t;

// Registration stayed at version 4
PG_REGISTER_WITH_RESET_TEMPLATE(blackboxConfig_t, blackboxConfig, PG_BLACKBOX_CONFIG, 4);

// Problem: Users with v4 settings have 4-byte struct layout
// New firmware expects 3-byte struct (invertedCardDetection removed)
// Result: Settings corruption - fields misaligned

// Fix: Increment to version 5
PG_REGISTER_WITH_RESET_TEMPLATE(blackboxConfig_t, blackboxConfig, PG_BLACKBOX_CONFIG, 5);

// Now: pgLoad() sees v4 settings, knows they're incompatible, uses defaults
```

## Success Criteria

- [ ] Documentation created in `claude/developer/docs/parameter_groups/`
- [ ] PR #11236 case study clearly explains version increment requirement
- [ ] Version increment rules documented with examples
- [ ] __pg_registry_* mechanism explained
- [ ] settings.yaml relationship documented
- [ ] Code examples are accurate and tested
- [ ] Cross-references to relevant source files included

## Related

- **PR:** [#11236](https://github.com/iNavFlight/inav/pull/11236) - Blackbox setting removal
- **Key Files:**
  - `src/main/config/parameter_group.h` - Core PG system
  - `src/main/blackbox/blackbox.h` - Example PG declaration
  - `src/main/blackbox/blackbox.c` - Example PG registration
  - `src/main/fc/settings.yaml` - User-facing settings

## Notes

This documentation should serve as the definitive reference for developers working with the PG system. It should answer the question "when do I increment the version?" clearly and unambiguously.

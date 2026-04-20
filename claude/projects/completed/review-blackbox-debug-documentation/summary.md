# Project: Review and Update Blackbox DEBUG Documentation

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Documentation Review / Update
**Created:** 2026-01-11
**Estimated Effort:** 2-3 hours

## Overview

Review existing documentation for blackbox DEBUG functionality (where users can select which debug fields get logged to blackbox), compare it against the actual implementation in the firmware code, and update documentation to accurately reflect the feature.

## Problem

Blackbox DEBUG is a powerful feature that allows users to select specific debug fields for logging, but the documentation may not adequately explain:
- How to select debug fields
- What debug fields are available
- How to configure DEBUG logging in blackbox
- What the debug data means

Users need clear, complete documentation to effectively use this feature.

## Solution

Use the `inav-architecture` agent to:
1. Search documentation sources for blackbox DEBUG information
2. Locate the implementation in the firmware code (debug field selection, blackbox logging)
3. Compare documentation against implementation
4. Update documentation where needed to accurately reflect the code and provide clear usage guidance

## Implementation

### Phase 1: Documentation Search
- Use `inav-architecture` agent to search `inav/docs/` directory for blackbox DEBUG references
- Use `inav-architecture` agent to search `inavwiki/` for blackbox DEBUG references
- Document where information is found and what it currently explains

### Phase 2: Code Analysis
- Use `inav-architecture` agent to find blackbox DEBUG implementation
- Understand how debug field selection works
- Identify what debug fields are available
- Document the actual functionality

### Phase 3: Comparison and Update
- Compare documentation vs implementation
- Identify gaps in documentation (missing debug fields, unclear usage instructions, etc.)
- Update documentation files to match implementation
- Add usage examples if missing
- Ensure documentation is clear and comprehensive

## Files to Check

**Documentation:**
- `inav/docs/` - Markdown documentation files (look for blackbox, debug, logging)
- `inavwiki/` - Wiki repository

**Code:**
- Files containing blackbox debug implementation
- Debug field definitions
- Configuration/settings files related to debug logging

## Success Criteria

- [ ] All blackbox DEBUG documentation locations identified
- [ ] Code implementation understood and documented
- [ ] Available debug fields catalogued
- [ ] Documentation compared against implementation
- [ ] Any needed documentation updates made
- [ ] Documentation provides clear usage guidance
- [ ] Documentation accurately reflects code behavior

## Related

- **Assignment:** `claude/manager/email/sent/2026-01-11-task-review-blackbox-debug-documentation.md`

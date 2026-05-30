# Project: Investigate OpenCode Compaction Context Loss

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Investigation / Bug Fix
**Created:** 2026-05-27
**Estimated Effort:** 3-6 hours

## Overview

Investigate and fix an issue where OpenCode loses task context during conversation compaction. After compressing earlier history to manage the context window, the agent loses track of the current task state and reverts to the first incomplete todo item.

## Problem

During long development sessions, OpenCode performs context compaction. After compaction, the agent can no longer answer the current query — instead it restarts work from the first incomplete todo item. This causes wasted work, confusion, and repeated cycles.

## Objectives

1. Understand how OpenCode's context compaction mechanism works
2. Understand how TodoWrite tool state interacts with compaction
3. Determine if current task context can be preserved across compactions
4. Implement a fix or workaround

## Scope

**In Scope:**
- OpenCode's context compaction behavior
- TodoWrite tool state persistence
- Plugin, skill, or configuration changes within inav-claude project

**Out of Scope:**
- Modifying OpenCode itself (not our project)
- Other OpenCode behaviors not related to compaction

## Implementation Steps

1. Research OpenCode's context compaction mechanism and documentation
2. Reproduce the issue with a test scenario
3. Identify root cause of context loss
4. Design and implement fix (skill modification, configuration, or workflow change)
5. Test the fix

## Success Criteria

- [ ] Root cause of context loss after compaction identified
- [ ] Fix or workaround implemented and tested
- [ ] Documentation updated in relevant claude/ files

## Related

- **Issue:** N/A
- **Request:** `manager/email/inbox/2026-05-27-1000-project-request-investigate-opencode-compaction-context-loss.md`

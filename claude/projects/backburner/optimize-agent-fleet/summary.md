# Project: Optimize Agent Fleet Token Consumption

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM-HIGH
**Type:** Optimization / Infrastructure
**Created:** 2026-02-15
**Estimated Time:** TBD — not yet scoped in detail

## Overview

Reduce Claude agent fleet token consumption by 60-70%. Three agents — `inav-architecture`, `target-developer`, `aerodynamics-expert` — are each consuming 20,000+ tokens per call, driving up cost and latency for routine lookups.

## Problem

These three agents load large reference material (architecture maps, target configs, aerodynamics textbook content) fresh on every invocation rather than reusing prior work, making even simple queries expensive.

## Objectives

1. Add caching so repeated/similar queries don't re-derive the same context
2. Build lightweight indexes (rather than full-content loads) for architecture and target lookups
3. Reassess model selection per agent — smaller/faster models where full capability isn't needed

## Scope

**In Scope:**
- `inav-architecture`, `target-developer`, `aerodynamics-expert` agent definitions and their supporting reference data
- Caching strategy (session-level or persistent)
- Indexing approach for faster targeted lookups

**Out of Scope:**
- Other agents not currently flagged as high-consumption

## Success Criteria

- [ ] Measured 60-70% reduction in average token consumption per call for the three target agents
- [ ] No regression in answer quality/accuracy for typical queries
- [ ] Caching/indexing approach documented for future agent additions

## Priority Justification

Meaningful cost/latency win across a repo where these agents are invoked frequently, but an infrastructure improvement rather than user-facing feature — deprioritized behind active DroneCAN feature work.

## Dependencies

None known. Not yet assigned or discussed with developer beyond this outline — backfilled 2026-07-07 from the INDEX.md description to give this project actual doc files (previously just an empty directory).
